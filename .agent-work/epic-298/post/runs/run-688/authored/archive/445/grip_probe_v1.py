"""#487 grip-frontier FIRST LOOK (scratch, untracked).

Silverstone 2023 Q, VER, pooled flying-lap apexes. Plots a_lat vs v with PVA-
propagated sigma error bars, colored by |a_long| (so we can SEE whether apexes
sit on the pure-lateral slice, a_long~0). Faint gray = all cornering samples
(a_lat>A_THR) for frontier context; colored = the apex (min-speed) points the
grip fit would consume.

sigma propagation: full anisotropic 4x4 (vx,vy,ax,ay) covariance block from the
smoother posterior (the adapter's cov_i_j cols; vx=3,vy=4,ax=6,ay=7), delta
method on a_lat=|vx*ay-vy*ax|/V and v=|(vx,vy)|. Cross terms kept (the along-
track timing inflation must project OUT of cross-track a_lat).
"""
import sys, warnings, logging
sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import fastf1
fastf1.Cache.enable_cache(r'C:\Programs\f1Brainz\outputs\cache')

from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session, stint_span
from src.preprocessing.trajectory.calibration import calibrate_session_hp, fit_lap
from src.preprocessing.trajectory.physics_adapter import smoother_to_processed_telemetry

G = 9.81
A_THR = 5.0   # m/s^2 cornering threshold
CAR = 'VER'
OUT = r'C:\Programs\f1Brainz\.agent-work\445\grip_silverstone_ver.png'


def derive(df):
    """Return v, |a_lat|, a_long (m/s^2) and sigma_v, sigma_alat per row."""
    vx = df['vx'].to_numpy(); vy = df['vy'].to_numpy()
    ax = df['ax'].to_numpy(); ay = df['ay'].to_numpy()
    V = np.maximum(np.hypot(vx, vy), 1e-6)
    s = vx * ay - vy * ax                       # signed cross product
    alat = s / V                                # signed lateral (centripetal)
    along = (vx * ax + vy * ay) / V             # tangential

    def c(i, j):
        i, j = min(i, j), max(i, j)
        return df[f'cov_{i}_{j}'].to_numpy()

    # d(s/V)/d{vx,vy,ax,ay}
    dvx = ay / V - s * vx / V**3
    dvy = -ax / V - s * vy / V**3
    dax = -vy / V
    day = vx / V
    var_alat = (dvx**2*c(3,3) + dvy**2*c(4,4) + dax**2*c(6,6) + day**2*c(7,7)
                + 2*dvx*dvy*c(3,4) + 2*dvx*dax*c(3,6) + 2*dvx*day*c(3,7)
                + 2*dvy*dax*c(4,6) + 2*dvy*day*c(4,7) + 2*dax*day*c(6,7))
    jvx, jvy = vx / V, vy / V
    var_v = jvx**2*c(3,3) + jvy**2*c(4,4) + 2*jvx*jvy*c(3,4)
    return V, np.abs(alat), along, np.sqrt(np.maximum(var_v, 0)), np.sqrt(np.maximum(var_alat, 0))


def apex_idx(V, alat):
    """min-speed point within each contiguous a_lat>A_THR run (>=3 samples)."""
    corner = alat > A_THR
    out = []; i = 0; n = len(V)
    while i < n:
        if corner[i]:
            j = i
            while j < n and corner[j]:
                j += 1
            run = np.arange(i, j)
            if len(run) >= 3:
                out.append(int(run[np.argmin(V[run])]))
            i = j
        else:
            i += 1
    return out


def main():
    q = load_session(2023, 'Great Britain', 'Q')
    num = driver_num(q, CAR)
    pos_d, spd_d = driver_streams(q, num)
    laps = q.laps.pick_drivers(CAR)
    valid = laps[laps['LapTime'].notna()]
    best = valid['LapTime'].dt.total_seconds().min()
    fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
    stint = int(fast['Stint'])
    st0, st1, _ = stint_span(q, CAR, stint, pad=2.0)
    mp = (pos_d['t'] >= st0) & (pos_d['t'] <= st1)
    mc = (spd_d['t'] >= st0) & (spd_d['t'] <= st1)
    hp = calibrate_session_hp(pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp],
                              spd_d['t'][mc], spd_d['V'][mc], order=4)
    print(f"{CAR} Silverstone: best={best:.2f}s  ell={hp.ell:.2f} nu={hp.nu}")

    # Pool flying laps across ALL stints (Q1/Q2/Q3 runs) for a fuller cloud.
    # NOTE: mixes track-evolution / tyre-life states slightly -- fine for a first
    # look at the frontier method; revisit if grip drifts across runs.
    flying = valid[valid['LapTime'].dt.total_seconds() <= 1.08 * best]
    span_cache = {}
    def stint_bounds(sn):
        if sn not in span_cache:
            s0, s1, _ = stint_span(q, CAR, sn, pad=2.0)
            span_cache[sn] = (s0, s1)
        return span_cache[sn]
    aV = []; aA = []; aAL = []; aSV = []; aSA = []           # apex
    cV = []; cA = []                                          # all cornering (context)
    for _, lap in flying.iterrows():
        lt0 = float(lap['LapStartTime'].total_seconds()); lt1 = float(lap['Time'].total_seconds())
        s0, s1 = stint_bounds(int(lap['Stint']))
        try:
            ss, info = fit_lap(pos_d, spd_d, lt0, lt1, hp, overhang=8.0, bounds=(s0, s1))
            df = smoother_to_processed_telemetry(ss, info['lap_t'])
        except Exception as e:
            print("  lap skip:", e); continue
        V, alat, along, sv, sa = derive(df)
        corner = alat > A_THR
        cV.extend(V[corner]); cA.extend(alat[corner])
        for k in apex_idx(V, alat):
            aV.append(V[k]); aA.append(alat[k]); aAL.append(along[k]); aSV.append(sv[k]); aSA.append(sa[k])

    aV, aA, aAL, aSV, aSA = map(np.array, (aV, aA, aAL, aSV, aSA))
    cV, cA = np.array(cV), np.array(cA)
    print(f"apexes={len(aV)} over {len(flying)} flying laps; "
          f"v {aV.min():.0f}-{aV.max():.0f} m/s; a_lat {aA.min()/G:.1f}-{aA.max()/G:.1f} g; "
          f"|a_long| at apex: med {np.median(np.abs(aAL))/G:.2f} g, p90 {np.percentile(np.abs(aAL),90)/G:.2f} g")
    print(f"sigma_alat: med {np.median(aSA)/G:.3f} g, p90 {np.percentile(aSA,90)/G:.3f} g; "
          f"sigma_v: med {np.median(aSV):.2f} m/s")

    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    ax.scatter(cV*3.6, cA/G, s=6, c='0.78', zorder=1, label='all cornering samples (a_lat>0.5g)')
    ax.errorbar(aV*3.6, aA/G, xerr=aSV*3.6, yerr=aSA/G, fmt='none', ecolor='0.5', alpha=0.5, zorder=2)
    sc = ax.scatter(aV*3.6, aA/G, c=np.abs(aAL)/G, cmap='viridis', s=48, zorder=3,
                    edgecolor='k', linewidth=0.3, label='apex (min-speed) points')
    cb = plt.colorbar(sc); cb.set_label('|a_long| at apex (g)   — near 0 = pure-lateral slice')
    ax.set_xlabel('apex speed (km/h)'); ax.set_ylabel('lateral accel  a_lat  (g)')
    ax.set_title(f'Silverstone 2023 Q — {CAR}: apex cloud (pooled flying laps)\n'
                 f'a_lat vs v, PVA-propagated sigma bars, colour=|a_long|')
    ax.grid(alpha=0.3); ax.legend(loc='lower left', fontsize=8)
    plt.tight_layout(); plt.savefig(OUT, dpi=130)
    print("wrote", OUT)


if __name__ == '__main__':
    main()

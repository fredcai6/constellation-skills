"""#487 grip frontier — three tracks: Silverstone, Spa, Hungary (scratch).

Cross-track test of the single-session fit. The hypothesis: the tyre CEILING and
the AERO coefficient are CAR/TYRE properties (should agree across the two wide-band
tracks), while only narrow-band Hungary fails to identify them. If Silverstone and
Spa agree on ceiling ~5.4g + a consistent aero, the parameters are poolable -> the
Epic-2 season prior premise holds.
"""
import os, sys, warnings, logging
sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

G = 9.81; A_THR = 5.0; RATIO = 0.2; NBOOT = 150
OUT = r'C:\Programs\f1Brainz\.agent-work\445\grip_three_tracks.png'
AW = r'C:\Programs\f1Brainz\.agent-work\445'
TRACKS = [('Great Britain', 'Silverstone', f'{AW}\\grip_cloud_silverstone_ver.npz'),
          ('Belgium',       'Spa',         f'{AW}\\grip_cloud_spa_ver.npz'),
          ('Hungary',       'Hungary',     f'{AW}\\grip_cloud_hungary_ver.npz')]


def derive(df):
    vx = df['vx'].to_numpy(); vy = df['vy'].to_numpy()
    ax = df['ax'].to_numpy(); ay = df['ay'].to_numpy()
    V = np.maximum(np.hypot(vx, vy), 1e-6); s = vx*ay - vy*ax
    alat = s/V; along = (vx*ax + vy*ay)/V
    def c(i, j):
        i, j = min(i, j), max(i, j); return df[f'cov_{i}_{j}'].to_numpy()
    dvx = ay/V - s*vx/V**3; dvy = -ax/V - s*vy/V**3; dax = -vy/V; day = vx/V
    var = (dvx**2*c(3,3)+dvy**2*c(4,4)+dax**2*c(6,6)+day**2*c(7,7)
           +2*dvx*dvy*c(3,4)+2*dvx*dax*c(3,6)+2*dvx*day*c(3,7)
           +2*dvy*dax*c(4,6)+2*dvy*day*c(4,7)+2*dax*day*c(6,7))
    return V, np.abs(alat), along, np.sqrt(np.maximum(var, 0))


def apex_idx(V, alat):
    corner = alat > A_THR; out = []; i = 0; n = len(V)
    while i < n:
        if corner[i]:
            j = i
            while j < n and corner[j]: j += 1
            run = np.arange(i, j)
            if len(run) >= 3: out.append(int(run[np.argmin(V[run])]))
            i = j
        else: i += 1
    return out


def extract(gp, npz):
    if os.path.exists(npz):
        d = np.load(npz); return d['v'], d['alat'], d['along'], d['sa']
    import fastf1; fastf1.Cache.enable_cache(r'C:\Programs\f1Brainz\outputs\cache')
    from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session, stint_span
    from src.preprocessing.trajectory.calibration import calibrate_session_hp, fit_lap
    from src.preprocessing.trajectory.physics_adapter import smoother_to_processed_telemetry
    q = load_session(2023, gp, 'Q'); num = driver_num(q, 'VER')
    pos_d, spd_d = driver_streams(q, num)
    valid = q.laps.pick_drivers('VER'); valid = valid[valid['LapTime'].notna()]
    best = valid['LapTime'].dt.total_seconds().min()
    fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
    st0, st1, _ = stint_span(q, 'VER', int(fast['Stint']), pad=2.0)
    mp = (pos_d['t']>=st0)&(pos_d['t']<=st1); mc = (spd_d['t']>=st0)&(spd_d['t']<=st1)
    hp = calibrate_session_hp(pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp], spd_d['t'][mc], spd_d['V'][mc], order=4)
    flying = valid[valid['LapTime'].dt.total_seconds() <= 1.08*best]; span = {}
    aV=[]; aA=[]; aAL=[]; aSA=[]
    for _, lap in flying.iterrows():
        sn = int(lap['Stint'])
        if sn not in span: s0,s1,_ = stint_span(q,'VER',sn,pad=2.0); span[sn]=(s0,s1)
        s0,s1 = span[sn]
        try:
            ss, info = fit_lap(pos_d, spd_d, float(lap['LapStartTime'].total_seconds()),
                               float(lap['Time'].total_seconds()), hp, overhang=8.0, bounds=(s0,s1))
            df = smoother_to_processed_telemetry(ss, info['lap_t'])
        except Exception as e:
            print('  skip', e); continue
        V, alat, along, sa = derive(df)
        for k in apex_idx(V, alat):
            aV.append(V[k]); aA.append(alat[k]); aAL.append(along[k]); aSA.append(sa[k])
    aV,aA,aAL,aSA = map(np.array,(aV,aA,aAL,aSA)); np.savez(npz, v=aV, alat=aA, along=aAL, sa=aSA)
    return aV,aA,aAL,aSA


def nll(p, v2, y, sig):
    mech, aero, ceil, lsu = p
    if ceil <= 0: return 1e18
    su = np.exp(lsu); e = y - np.minimum(mech + aero*v2, ceil)
    s = np.sqrt(sig**2 + su**2); lam = su/np.maximum(sig,1e-9)
    return -np.sum(np.log(2) - np.log(s) + norm.logpdf(e/s) + norm.logcdf(-lam*e/s))


def fit(v2, y, sig, p0):
    return minimize(nll, p0, args=(v2,y,sig), method='Nelder-Mead',
                    options=dict(maxiter=4000, xatol=1e-6, fatol=1e-6)).x


def analyse(gp, npz):
    aV, aA, aAL, aSA = extract(gp, npz)
    keep = np.abs(aAL)/np.maximum(aA,1e-6) < RATIO
    V, A, SA = aV[keep], aA[keep], aSA[keep]; v2 = V**2; n = len(V)
    p0 = [3.2*G, 4e-3, max(A)*1.02, np.log(1.6*G)]
    p = fit(v2, A, SA, p0)
    rng = np.random.default_rng(0); B=[]
    for _ in range(NBOOT):
        idx = rng.integers(0, n, n)
        try: B.append(fit(v2[idx], A[idx], SA[idx], p))
        except Exception: pass
    B = np.array(B)
    return dict(V=V, A=A, SA=SA, ratio=keep.sum() and (np.abs(aAL)/np.maximum(aA,1e-6))[keep],
                mech=p[0], aero=p[1], ceil=p[2], su=np.exp(p[3]),
                mech_sd=B[:,0].std(), aero_sd=B[:,1].std(), ceil_sd=B[:,2].std(), boots=B, n=n)


def main():
    R = {lab: analyse(gp, npz) for gp, lab, npz in TRACKS}
    print(f"\n{'track':>12} {'n':>4} {'v-range km/h':>14} {'mech g':>10} {'aero':>16} {'ceiling g':>14}")
    for _, lab, _ in TRACKS:
        r = R[lab]
        print(f"{lab:>12} {r['n']:>4} {r['V'].min()*3.6:>6.0f}-{r['V'].max()*3.6:<6.0f} "
              f"{r['mech']/G:>5.2f}+-{r['mech_sd']/G:<.2f} "
              f"{r['aero']:>8.1e}+-{r['aero_sd']:.0e}({abs(r['aero_sd']/r['aero'])*100:>3.0f}%) "
              f"{r['ceil']/G:>5.2f}+-{r['ceil_sd']/G:<.2f}")

    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(17, 5.6), sharey=True)
    for ax, (_, lab, _) in zip(axs, TRACKS):
        r = R[lab]; V, A, SA = r['V'], r['A'], r['SA']
        vg = np.linspace(V.min(), V.max(), 200); v2g = vg**2
        fr = np.minimum(r['mech'] + r['aero']*v2g, r['ceil'])
        frb = np.array([np.minimum(b[0]+b[1]*v2g, b[2]) for b in r['boots']])
        lo, hi = np.percentile(frb, [16, 84], axis=0)
        ax.scatter(V*3.6, A/G, c=r['ratio'], cmap='viridis', s=30, zorder=3, edgecolor='k', lw=0.3)
        ax.errorbar(V*3.6, A/G, yerr=SA/G, fmt='none', ecolor='0.6', alpha=0.3, zorder=2)
        ax.plot(vg*3.6, fr/G, 'C3-', lw=2.6, zorder=5)
        ax.fill_between(vg*3.6, lo/G, hi/G, color='C3', alpha=0.18, zorder=1)
        ax.axhline(r['ceil']/G, color='0.4', ls='--', lw=0.8)
        unc = abs(r['aero_sd']/r['aero'])*100
        ax.set_title(f"{lab}\nmech {r['mech']/G:.1f}g · aero ±{unc:.0f}% · ceiling {r['ceil']/G:.1f}g", fontsize=10)
        ax.set_xlabel('apex speed (km/h)'); ax.grid(alpha=0.3)
    axs[0].set_ylabel('lateral grip used  a_lat  (g)')
    fig.suptitle('Single-session grip frontier across three tracks — VER 2023 Q\n'
                 '(ceiling + aero should agree on the two wide-band tracks if they are car/tyre properties)',
                 fontsize=12)
    plt.tight_layout(); plt.savefig(OUT, dpi=130, bbox_inches='tight'); print('\nwrote', OUT)


if __name__ == '__main__':
    main()

"""#487 grip-frontier STOCHASTIC-FRONTIER FIT (scratch, untracked).

Caches the apex cloud (extraction is the slow part) to npz, then:
  - filters to pure-lateral apexes |a_long|/|a_lat| < RATIO
  - fits a_lat = A0 + B*v^2 - u + eps   (B = A2*rho)
        eps_i ~ N(0, sigma_i^2)  KNOWN per-apex (PVA-propagated)
        u_i   ~ HalfNormal(sigma_u)  one-sided utilisation gap (>=0)
    via heteroscedastic stochastic-frontier MLE (Aigner-Lovell-Schmidt density).
  - overlays the naive OLS fit (the production-style central fit) to show the slope.
Gsat OFF for this first fit.
"""
import sys, os, warnings, logging
sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.stats import norm

G = 9.81
A_THR = 5.0
RATIO = 0.2
CAR = 'VER'
NPZ = r'C:\Programs\f1Brainz\.agent-work\445\grip_cloud_silverstone_ver.npz'
OUT = r'C:\Programs\f1Brainz\.agent-work\445\grip_sfa_silverstone_ver.png'


def derive(df):
    vx = df['vx'].to_numpy(); vy = df['vy'].to_numpy()
    ax = df['ax'].to_numpy(); ay = df['ay'].to_numpy()
    V = np.maximum(np.hypot(vx, vy), 1e-6)
    s = vx*ay - vy*ax
    alat = s/V; along = (vx*ax + vy*ay)/V
    def c(i, j):
        i, j = min(i, j), max(i, j); return df[f'cov_{i}_{j}'].to_numpy()
    dvx = ay/V - s*vx/V**3; dvy = -ax/V - s*vy/V**3; dax = -vy/V; day = vx/V
    var_alat = (dvx**2*c(3,3)+dvy**2*c(4,4)+dax**2*c(6,6)+day**2*c(7,7)
                +2*dvx*dvy*c(3,4)+2*dvx*dax*c(3,6)+2*dvx*day*c(3,7)
                +2*dvy*dax*c(4,6)+2*dvy*day*c(4,7)+2*dax*day*c(6,7))
    jvx, jvy = vx/V, vy/V
    var_v = jvx**2*c(3,3)+jvy**2*c(4,4)+2*jvx*jvy*c(3,4)
    return V, np.abs(alat), along, np.sqrt(np.maximum(var_v,0)), np.sqrt(np.maximum(var_alat,0))


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


def extract_cloud():
    import fastf1
    fastf1.Cache.enable_cache(r'C:\Programs\f1Brainz\outputs\cache')
    from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session, stint_span
    from src.preprocessing.trajectory.calibration import calibrate_session_hp, fit_lap
    from src.preprocessing.trajectory.physics_adapter import smoother_to_processed_telemetry
    q = load_session(2023, 'Great Britain', 'Q'); num = driver_num(q, CAR)
    pos_d, spd_d = driver_streams(q, num)
    valid = q.laps.pick_drivers(CAR); valid = valid[valid['LapTime'].notna()]
    best = valid['LapTime'].dt.total_seconds().min()
    fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
    st0, st1, _ = stint_span(q, CAR, int(fast['Stint']), pad=2.0)
    mp = (pos_d['t']>=st0)&(pos_d['t']<=st1); mc = (spd_d['t']>=st0)&(spd_d['t']<=st1)
    hp = calibrate_session_hp(pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp], spd_d['t'][mc], spd_d['V'][mc], order=4)
    flying = valid[valid['LapTime'].dt.total_seconds() <= 1.08*best]
    span = {}
    aV=[]; aA=[]; aAL=[]; aSV=[]; aSA=[]
    for _, lap in flying.iterrows():
        sn = int(lap['Stint'])
        if sn not in span: s0,s1,_ = stint_span(q,CAR,sn,pad=2.0); span[sn]=(s0,s1)
        s0,s1 = span[sn]
        try:
            ss, info = fit_lap(pos_d, spd_d, float(lap['LapStartTime'].total_seconds()),
                               float(lap['Time'].total_seconds()), hp, overhang=8.0, bounds=(s0,s1))
            df = smoother_to_processed_telemetry(ss, info['lap_t'])
        except Exception as e:
            print('  lap skip', e); continue
        V, alat, along, sv, sa = derive(df)
        for k in apex_idx(V, alat):
            aV.append(V[k]); aA.append(alat[k]); aAL.append(along[k]); aSV.append(sv[k]); aSA.append(sa[k])
    aV,aA,aAL,aSV,aSA = map(np.array,(aV,aA,aAL,aSV,aSA))
    np.savez(NPZ, v=aV, alat=aA, along=aAL, sv=aSV, sa=aSA)
    return aV,aA,aAL,aSV,aSA


def sfa_nll(p, v2, y, sig):
    A0, B, lsu = p; su = np.exp(lsu)
    e = y - (A0 + B*v2)
    s = np.sqrt(sig**2 + su**2); lam = su/np.maximum(sig,1e-9)
    return -np.sum(np.log(2) - np.log(s) + norm.logpdf(e/s) + norm.logcdf(-lam*e/s))


def main():
    if os.path.exists(NPZ):
        d = np.load(NPZ); aV,aA,aAL,aSV,aSA = d['v'],d['alat'],d['along'],d['sv'],d['sa']
        print(f"loaded cached cloud: {len(aV)} apexes")
    else:
        aV,aA,aAL,aSV,aSA = extract_cloud(); print(f"extracted {len(aV)} apexes")

    ratio = np.abs(aAL)/np.maximum(aA,1e-6)
    keep = ratio < RATIO
    V,A,SV,SA = aV[keep],aA[keep],aSV[keep],aSA[keep]
    print(f"pure-lateral cut |a_long|/|a_lat|<{RATIO}: kept {keep.sum()}/{len(aV)}")
    v2 = V**2

    # naive OLS (production-style central fit)
    Xo = np.column_stack([np.ones_like(v2), v2])
    bo, *_ = np.linalg.lstsq(Xo, A, rcond=None); A0o, Bo = bo

    # SFA MLE
    res = minimize(sfa_nll, [A0o, max(Bo,1e-5), np.log(np.std(A))], args=(v2,A,SA),
                   method='BFGS')
    A0,B,lsu = res.x; su = np.exp(lsu)
    cov = res.hess_inv[:2,:2]  # (A0,B) covariance
    sA0,sB = np.sqrt(np.diag(cov)); rho_ab = cov[0,1]/(sA0*sB)
    print(f"OLS : A0={A0o/G:.2f}g  B={Bo:.2e} 1/m")
    print(f"SFA : A0={A0/G:.2f}+-{sA0/G:.2f}g  B={B:.2e}+-{sB:.2e} 1/m  corr(A0,B)={rho_ab:+.2f}  sigma_u={su/G:.2f}g")
    print(f"frontier@300km/h = {(A0+B*(300/3.6)**2)/G:.2f}g   @100km/h = {(A0+B*(100/3.6)**2)/G:.2f}g")

    vg = np.linspace(V.min(), V.max(), 200); v2g = vg**2
    front = A0 + B*v2g
    Jf = np.column_stack([np.ones_like(v2g), v2g])
    sfront = np.sqrt(np.einsum('ij,jk,ik->i', Jf, cov, Jf))

    fig, ax = plt.subplots(figsize=(9.5,6.2))
    sc = ax.scatter(V*3.6, A/G, c=ratio[keep], cmap='viridis', s=42, zorder=3, edgecolor='k', lw=0.3)
    ax.errorbar(V*3.6, A/G, yerr=SA/G, fmt='none', ecolor='0.5', alpha=0.4, zorder=2)
    ax.plot(vg*3.6, front/G, 'C3-', lw=2.4, zorder=4, label=f'SFA frontier  A0={A0/G:.2f}g, B={B:.1e}')
    ax.fill_between(vg*3.6, (front-sfront)/G, (front+sfront)/G, color='C3', alpha=0.2, zorder=1)
    ax.plot(vg*3.6, (A0o+Bo*v2g)/G, 'C0--', lw=1.8, zorder=4, label=f'naive OLS  A0={A0o/G:.2f}g, B={Bo:.1e}')
    cb = plt.colorbar(sc); cb.set_label('|a_long|/|a_lat| (kept < 0.2)')
    ax.set_xlabel('apex speed (km/h)'); ax.set_ylabel('lateral accel a_lat (g)')
    ax.set_title(f'Silverstone 2023 Q — {CAR}: stochastic-frontier grip fit\n'
                 f'pure-lateral apexes; SFA (frontier+slack) vs naive OLS (central)')
    ax.grid(alpha=0.3); ax.legend(loc='upper left', fontsize=9)
    plt.tight_layout(); plt.savefig(OUT, dpi=130); print('wrote', OUT)


if __name__ == '__main__':
    main()

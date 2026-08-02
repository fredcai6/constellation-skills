"""#487 grip frontier WITH tyre-saturation ceiling (scratch, untracked).

Loads the cached apex cloud, filters to pure-lateral apexes, fits

    a_lat = min( mech_grip + aero*v^2 , ceiling ) - u + eps
        eps_i ~ N(0, sigma_i^2)  KNOWN per-apex (measurement)
        u_i   ~ HalfNormal(util_spread)  one-sided (corner taken below the limit)

via heteroscedastic stochastic-frontier MLE.  Parameters in plain terms:
    mech_grip   = slow-corner / v=0 mechanical grip          (g)
    aero        = extra grip per speed^2 (downforce term)    (1/m, = A2*rho)
    ceiling     = tyre saturation ceiling (Gsat)             (g)
    util_spread = how far below the limit corners are taken  (g)
Uncertainties + frontier band via bootstrap (robust to the min() kink).
"""
import os, warnings
warnings.filterwarnings('ignore')
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

G = 9.81
RATIO = 0.2
NPZ = r'C:\Programs\f1Brainz\.agent-work\445\grip_cloud_silverstone_ver.npz'
OUT = r'C:\Programs\f1Brainz\.agent-work\445\grip_gsat_silverstone_ver.png'
NBOOT = 150


def nll(p, v2, y, sig):
    mech, aero, ceil, lsu = p
    if aero < 0 or ceil <= 0:
        return 1e18
    su = np.exp(lsu)
    front = np.minimum(mech + aero * v2, ceil)
    e = y - front
    s = np.sqrt(sig**2 + su**2)
    lam = su / np.maximum(sig, 1e-9)
    return -np.sum(np.log(2) - np.log(s) + norm.logpdf(e / s) + norm.logcdf(-lam * e / s))


def fit(v2, y, sig, p0):
    r = minimize(nll, p0, args=(v2, y, sig), method='Nelder-Mead',
                 options=dict(maxiter=4000, xatol=1e-6, fatol=1e-6))
    return r.x


def main():
    d = np.load(NPZ)
    aV, aA, aAL, aSA = d['v'], d['alat'], d['along'], d['sa']
    keep = np.abs(aAL) / np.maximum(aA, 1e-6) < RATIO
    V, A, SA = aV[keep], aA[keep], aSA[keep]
    v2 = V**2
    n = len(V)
    print(f"{n} pure-lateral apexes")

    p0 = [3.5 * G, 3.7e-3, 5.4 * G, np.log(2.0 * G)]
    mech, aero, ceil, lsu = fit(v2, A, SA, p0)
    su = np.exp(lsu)

    # bootstrap for honest uncertainties + frontier band
    rng = np.random.default_rng(0)
    boots = []
    for _ in range(NBOOT):
        idx = rng.integers(0, n, n)
        try:
            boots.append(fit(v2[idx], A[idx], SA[idx], [mech, aero, ceil, lsu]))
        except Exception:
            pass
    boots = np.array(boots)
    bm, ba, bc, bl = boots[:, 0], boots[:, 1], boots[:, 2], np.exp(boots[:, 3])

    print(f"mechanical grip (v=0): {mech/G:.2f} +- {bm.std()/G:.2f} g")
    print(f"aero coefficient     : {aero:.2e} +- {ba.std():.2e}  (extra grip per v^2)")
    print(f"tyre ceiling (Gsat)  : {ceil/G:.2f} +- {bc.std()/G:.2f} g")
    print(f"utilisation spread   : {su/G:.2f} +- {bl.std()/G:.2f} g")
    corr = np.corrcoef(bm, ba)[0, 1]
    print(f"corr(mechanical, aero) over bootstraps: {corr:+.2f}")
    for kmh in (100, 200, 300):
        f = min(mech + aero * (kmh/3.6)**2, ceil) / G
        print(f"  frontier @ {kmh} km/h = {f:.2f} g")

    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    vg = np.linspace(V.min(), V.max(), 250); v2g = vg**2
    fr = np.minimum(mech + aero * v2g, ceil)
    fr_b = np.array([np.minimum(b[0] + b[1] * v2g, b[2]) for b in boots])
    lo, hi = np.percentile(fr_b, [16, 84], axis=0)
    # no-ceiling frontier for contrast
    fr_noceil = mech + aero * v2g

    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    sc = ax.scatter(V*3.6, A/G, c=(np.abs(aAL)/np.maximum(aA,1e-6))[keep], cmap='viridis',
                    s=42, zorder=3, edgecolor='k', lw=0.3)
    ax.errorbar(V*3.6, A/G, yerr=SA/G, fmt='none', ecolor='0.5', alpha=0.4, zorder=2)
    ax.plot(vg*3.6, fr/G, 'C3-', lw=2.6, zorder=5,
            label=f'frontier WITH tyre ceiling  (mech {mech/G:.1f}g, ceiling {ceil/G:.1f}g)')
    ax.fill_between(vg*3.6, lo/G, hi/G, color='C3', alpha=0.18, zorder=1)
    ax.plot(vg*3.6, fr_noceil/G, 'C3:', lw=1.4, alpha=0.7, zorder=4,
            label='same fit, ceiling removed (overshoots)')
    ax.axhline(ceil/G, color='0.4', ls='--', lw=0.8, zorder=1)
    cb = plt.colorbar(sc); cb.set_label('|a_long|/|a_lat|  (longitudinal contribution)')
    ax.set_xlabel('apex speed (km/h)'); ax.set_ylabel('lateral grip used  a_lat  (g)')
    ax.set_title('Silverstone 2023 Q — VER: lateral grip frontier with tyre ceiling\n'
                 'stochastic frontier (mechanical + aero, capped at the tyre limit)')
    ax.grid(alpha=0.3); ax.legend(loc='upper left', fontsize=9)
    plt.tight_layout(); plt.savefig(OUT, dpi=130); print('wrote', OUT)


if __name__ == '__main__':
    main()

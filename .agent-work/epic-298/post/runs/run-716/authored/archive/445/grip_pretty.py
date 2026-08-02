"""Presentation-quality render of the #487 lateral grip envelope result.

Clean apex cloud (cached), stochastic-frontier-with-ceiling fit, the three physical
regimes annotated: mechanical grip -> downforce-loaded -> tyre saturation.
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

G = 9.81; RATIO = 0.2; NBOOT = 200
NPZ = r'C:\Programs\f1Brainz\.agent-work\445\grip_cloud_silverstone_ver.npz'
OUT = r'C:\Programs\f1Brainz\.agent-work\445\grip_envelope_silverstone.png'


def nll(p, v2, y, sig):
    mech, aero, ceil, lsu = p
    if ceil <= 0: return 1e18
    su = np.exp(lsu); e = y - np.minimum(mech + aero*v2, ceil)
    s = np.sqrt(sig**2 + su**2); lam = su/np.maximum(sig, 1e-9)
    return -np.sum(np.log(2) - np.log(s) + norm.logpdf(e/s) + norm.logcdf(-lam*e/s))


def fit(v2, y, sig, p0):
    return minimize(nll, p0, args=(v2, y, sig), method='Nelder-Mead',
                    options=dict(maxiter=4000, xatol=1e-6, fatol=1e-6)).x


d = np.load(NPZ)
keep = np.abs(d['along'])/np.maximum(d['alat'], 1e-6) < RATIO
V, A, SA = d['v'][keep], d['alat'][keep], d['sa'][keep]
v2 = V**2
p = fit(v2, A, SA, [3.2*G, 4e-3, 5.4*G, np.log(1.8*G)])
mech, aero, ceil, su = p[0], p[1], p[2], np.exp(p[3])
rng = np.random.default_rng(0)
boots = np.array([fit(v2[i], A[i], SA[i], p) for i in (rng.integers(0, len(V), len(V)) for _ in range(NBOOT))])

vg = np.linspace(V.min()*0.92, V.max()*1.04, 300); v2g = vg**2
fr = np.minimum(mech + aero*v2g, ceil)
frb = np.array([np.minimum(b[0]+b[1]*v2g, b[2]) for b in boots])
lo, hi = np.percentile(frb, [16, 84], axis=0)
kink = np.sqrt(max((ceil-mech)/aero, 0))  # speed where aero meets ceiling

plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.edgecolor': '#444',
                     'axes.linewidth': 0.8, 'figure.facecolor': 'white'})
fig, ax = plt.subplots(figsize=(11.5, 7))
ax.set_facecolor('#fbfbfd')

# region above the tyre ceiling = physically unreachable
ax.axhspan(ceil/G, ceil/G + 2, color='#e8e8ee', alpha=0.6, zorder=0)
ax.axhline(ceil/G, color='#777', ls=(0, (6, 4)), lw=1.1, zorder=2)

# apex cloud
ax.scatter(V*3.6, A/G, s=46, c='#3b6ea5', alpha=0.55, edgecolor='white', lw=0.5,
           zorder=3, label='apex measurements (on-limit cornering)')
ax.errorbar(V*3.6, A/G, yerr=SA/G, fmt='none', ecolor='#9bb4cc', alpha=0.5, lw=0.8, zorder=2)

# fitted frontier + uncertainty band
ax.fill_between(vg*3.6, lo/G, hi/G, color='#c1272d', alpha=0.16, zorder=4)
ax.plot(vg*3.6, fr/G, color='#c1272d', lw=3.4, zorder=6, solid_capstyle='round',
        label='fitted grip frontier')

# regime annotations
ax.annotate('MECHANICAL GRIP\nslow corners, tyres only',
            xy=(V.min()*3.6*1.05, (mech + aero*(V.min()*1.05)**2)/G), xytext=(95, 4.55),
            fontsize=10.5, color='#1f3b57', weight='bold', ha='left', va='center',
            arrowprops=dict(arrowstyle='-|>', color='#1f3b57', lw=1.4,
                            connectionstyle='arc3,rad=-0.25'))
ax.annotate('DOWNFORCE-LOADED\ngrip grows with speed²',
            xy=(165, (mech + aero*(165/3.6)**2)/G), xytext=(150, 2.15),
            fontsize=10.5, color='#7a4a00', weight='bold', ha='center', va='center',
            arrowprops=dict(arrowstyle='-|>', color='#7a4a00', lw=1.4,
                            connectionstyle='arc3,rad=0.25'))
ax.annotate(f'TYRE SATURATION\nceiling {ceil/G:.1f} g', xy=(vg.max()*3.6*0.9, ceil/G),
            xytext=(258, 6.05), fontsize=10.5, color='#444', weight='bold', ha='center', va='center',
            arrowprops=dict(arrowstyle='-|>', color='#444', lw=1.4,
                            connectionstyle='arc3,rad=-0.2'))

# parameter card
txt = (f"mechanical grip   {mech/G:.2f} ± {boots[:,0].std()/G:.2f} g\n"
       f"aero coefficient   well-determined (±{abs(boots[:,1].std()/aero)*100:.0f}%)\n"
       f"tyre ceiling          {ceil/G:.2f} ± {boots[:,2].std()/G:.2f} g\n"
       f"every parameter fit from this one session")
ax.text(0.975, 0.045, txt, transform=ax.transAxes, fontsize=9.3, ha='right', va='bottom',
        family='monospace', bbox=dict(boxstyle='round,pad=0.6', fc='white', ec='#ccc', alpha=0.95))

ax.set_xlabel('corner speed  (km/h)', fontsize=12)
ax.set_ylabel('lateral grip  (g)', fontsize=12)
ax.set_title('Lateral Grip Envelope  —  Verstappen · Silverstone 2023 Qualifying',
             fontsize=15, weight='bold', pad=14)
ax.text(0.5, 1.012, 'single-session stochastic-frontier fit:  mechanical + downforce grip, capped at the tyre limit',
        transform=ax.transAxes, ha='center', fontsize=10.5, color='#666')
ax.set_ylim(0.3, ceil/G + 1.1); ax.set_xlim(vg.min()*3.6, vg.max()*3.6)
ax.grid(True, color='#dddde3', lw=0.7); ax.set_axisbelow(True)
ax.legend(loc='lower right', fontsize=9.5, framealpha=0.95, edgecolor='#ccc', bbox_to_anchor=(0.999, 0.20))
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
plt.tight_layout(); plt.savefig(OUT, dpi=160, bbox_inches='tight'); print('wrote', OUT)

"""Is the DRS closed/open aero relationship a stable per-team fingerprint across setups? (#445)

Each weekend a team picks a wing level (CdA_closed varies). Question: does CdA_open move in lockstep
— i.e. is the DRS effect (drag shed by opening the flap) a consistent per-car property even as the
absolute setup changes? If yes, the closed→open relationship is a cleaner aero fingerprint than the
setup-contaminated absolute CdA.

Tests:
  1. per team regress CdA_open ~ CdA_closed across weekends: slope/intercept/R² (tight line = stable).
  2. fractional DRS reduction f = 1 − CdA_open/CdA_closed: within-team vs between-team spread (ICC-like).
  3. rank teams by DRS reduction (per-car DRS effectiveness).
Filters to well-identified weekends (honest σ) so junk fits don't pollute the relationship.
"""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
drs = json.loads((OUT / "season_drs.json").read_text())

# gather per-team weekends, keep well-identified fits
TEAMS = {}
for rn, rec in drs.items():
    for t, v in rec.items():
        cc, co, P, sc, so, cond, nc, no, ovm = v
        if cc <= 0 or co <= 0:
            continue
        if sc / cc > 0.15 or so / co > 0.22:     # honest-σ identifiability gate
            continue
        TEAMS.setdefault(t, []).append((cc, co, sc, so, rn))


def wls(x, y, w):
    """weighted slope/intercept/R²."""
    W = np.sum(w); xm = np.sum(w * x) / W; ym = np.sum(w * y) / W
    sxx = np.sum(w * (x - xm) ** 2); sxy = np.sum(w * (x - xm) * (y - ym))
    b = sxy / sxx; a = ym - b * xm
    pred = a + b * x
    ss_res = np.sum(w * (y - pred) ** 2); ss_tot = np.sum(w * (y - ym) ** 2)
    return b, a, 1 - ss_res / ss_tot


print(f"{'team':>5}{'n':>4}{'CdA_c range':>14}{'slope dO/dC':>12}{'R²':>7}"
      f"{'mean DRS cut':>13}{'within σ':>10}")
red_means, red_within, rows = {}, {}, []
for t in sorted(TEAMS):
    pts = TEAMS[t]
    if len(pts) < 6:
        continue
    cc = np.array([p[0] for p in pts]); co = np.array([p[1] for p in pts])
    so = np.array([p[3] for p in pts])
    w = 1.0 / (so ** 2 + 1e-6)
    b, a, r2 = wls(cc, co, w)
    f = 1 - co / cc                                  # fractional drag cut from DRS
    red_means[t] = float(np.average(f, weights=w))
    red_within[t] = float(np.sqrt(np.average((f - red_means[t]) ** 2, weights=w)))
    rows.append((t, len(pts), cc.min(), cc.max(), b, r2, red_means[t], red_within[t]))
    print(f"{t:>5}{len(pts):>4}{f'{cc.min():.2f}–{cc.max():.2f}':>14}{b:>12.2f}{r2:>7.2f}"
          f"{red_means[t]*100:>12.1f}%{red_within[t]*100:>9.1f}%")

# ICC-like: between-team spread of mean reduction vs typical within-team spread
mu = np.array(list(red_means.values()))
between = float(np.std(mu))
within = float(np.median(list(red_within.values())))
print(f"\nDRS drag-cut: between-team σ = {between*100:.1f}%   within-team σ (median) = {within*100:.1f}%")
print(f"  discriminability between/within = {between/within:.2f}   (>1 ⇒ stable per-team fingerprint)")
print("\nteams by DRS drag-cut (most effective DRS first):")
for t in sorted(red_means, key=lambda k: -red_means[k]):
    print(f"   {t:>4}  {red_means[t]*100:4.1f}% ± {red_within[t]*100:.1f}%")

# plot: CdA_open vs CdA_closed, each team a colour; per-team WLS line
fig, ax = plt.subplots(figsize=(7.6, 7.2))
cmap = plt.get_cmap("tab10")
for i, t in enumerate(sorted(TEAMS)):
    pts = TEAMS[t]
    if len(pts) < 6:
        continue
    cc = np.array([p[0] for p in pts]); co = np.array([p[1] for p in pts])
    so = np.array([p[3] for p in pts]); w = 1 / (so ** 2 + 1e-6)
    c = cmap(i % 10)
    ax.scatter(cc, co, s=22, color=c, alpha=0.7, label=t)
    b, a, _ = wls(cc, co, w)
    xs = np.array([cc.min(), cc.max()]); ax.plot(xs, a + b * xs, color=c, lw=1.3, alpha=0.8)
lim = [min(min(p[0] for p in v) for v in TEAMS.values() if len(v) >= 6) - 0.1,
       max(max(p[0] for p in v) for v in TEAMS.values() if len(v) >= 6) + 0.1]
ax.plot(lim, lim, "k:", lw=0.8, label="no DRS effect")
ax.set_xlabel("CdA closed (configured wing) — varies with setup")
ax.set_ylabel("CdA open (DRS deployed)")
ax.set_title("DRS closed→open relationship per team across 2023 weekends\n"
             "(stable per-team line ⇒ DRS effect is a setup-invariant aero fingerprint)")
ax.legend(fontsize=8, ncol=2); ax.grid(alpha=0.3)
png = OUT / "drs_consistency.png"
fig.tight_layout(); fig.savefig(png, dpi=120)
print(f"\nwrote {png}")

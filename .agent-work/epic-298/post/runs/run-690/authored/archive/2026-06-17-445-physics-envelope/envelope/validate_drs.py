import json
from pathlib import Path
import numpy as np

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
drs = json.loads((OUT / "season_drs.json").read_text())
old = json.loads((OUT / "season_cda.json").read_text())   # closed-only joint-less CdA (real rho)
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# per-round honest-σ and conditioning summary (sorted by median cond = worst identifiability first)
rows = []
for rn, rec in drs.items():
    sc = [v[3] for v in rec.values()]; cd = [v[5] for v in rec.values()]
    cc = [v[0] for v in rec.values()]; ov = [v[8] for v in rec.values()]
    rows.append((np.median(cd), rn, np.median(cc), np.median(sc), np.median(ov)))
rows.sort(reverse=True)
print(f'{"round":<16}{"med cond":>9}{"med CdA_c":>10}{"med σ_c":>9}{"σ/CdA%":>8}{"open vmax":>10}')
for cd, rn, cc, sc, ov in rows:
    print(f"{rn:<16}{cd:>9.0f}{cc:>10.3f}{sc:>9.3f}{sc/cc*100:>8.1f}{ov:>10.0f}")

print("\n--- Mexico City: closed-only (old) vs JOINT (new), per team ---")
print(f'{"team":>5}{"CdA_c old":>11}{"CdA_c joint":>12}{"σ_c joint":>10}{"σ/CdA%":>8}{"cond":>8}')
mo = old.get("Mexico City", {}); mn = drs.get("Mexico City", {})
for t in sorted(mn, key=lambda k: mn[k][0]):
    o = mo.get(t, [None])[0]
    cc, _, _, sc, _, cond, *_ = mn[t]
    print(f"{t:>5}{(o if o is not None else float('nan')):>11.3f}{cc:>12.3f}{sc:>10.3f}{sc/cc*100:>8.1f}{cond:>8.0f}")

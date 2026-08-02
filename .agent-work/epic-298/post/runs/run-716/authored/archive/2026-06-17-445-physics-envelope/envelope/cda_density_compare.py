"""Before/after: fixed RHO=1.2 vs real per-session density on the season CdA (#445).
Reads season_cda_fixedrho.json (old) and season_cda.json (new) and reports the per-round CdA
shift, ordered by magnitude — the altitude tracks (Mexico, Sao Paulo, Austria) should move most.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
old = json.loads((OUT / "season_cda_fixedrho.json").read_text())
new = json.loads((OUT / "season_cda.json").read_text())
dens = json.loads((OUT / "session_density.json").read_text())

# map round-name -> density via the round index isn't stored in cda json; density keyed by round num
# build a name->rho by matching the collection order (rounds 1..22). Instead show per-round mean shift.
rows = []
for nm in new:
    if nm not in old:
        continue
    teams = [t for t in new[nm] if t in old[nm]]
    if not teams:
        continue
    ratios = [new[nm][t][0] / old[nm][t][0] for t in teams if old[nm][t][0]]
    rows.append((np.mean(ratios), nm, np.mean([new[nm][t][0] for t in teams]),
                 np.mean([old[nm][t][0] for t in teams]), len(teams)))

rows.sort(reverse=True)
print(f"{'round':<18}{'CdA_new/CdA_old':>16}{'mean CdA old':>14}{'mean CdA new':>14}{'teams':>7}")
for ratio, nm, mnew, mold, n in rows:
    flag = "  <-- altitude" if ratio > 1.10 else ""
    print(f"{nm:<18}{ratio:>16.3f}{mold:>14.3f}{mnew:>14.3f}{n:>7}{flag}")

# density table for reference
print("\nper-session density (rho), by round number:")
for k in sorted(dens, key=lambda x: int(x.split('|')[1])):
    yr, rn, ses = k.split("|")
    print(f"  round {int(rn):>2}: rho={dens[k]:.3f}")

import json
from pathlib import Path
import numpy as np

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
s = json.loads((OUT / "season_cda.json").read_text())
rows = []
for rn, rec in s.items():
    sig = [v[1] for v in rec.values() if v[1] is not None]
    cda = [v[0] for v in rec.values()]
    if sig:
        rows.append((np.median(sig), rn, np.median(cda), np.median(sig) / np.median(cda) * 100, len(sig)))
rows.sort(reverse=True)
flagged = {"Singapore", "Mexico City", "Dutch"}
print(f'{"round":<16}{"med sig":>9}{"med CdA":>9}{"sig/CdA%":>9}{"teams":>6}')
for sg, rn, cda, pct, n in rows:
    mark = "  <-- flagged" if rn in flagged else ""
    print(f"{rn:<16}{sg:>9.3f}{cda:>9.3f}{pct:>9.1f}{n:>6}{mark}")

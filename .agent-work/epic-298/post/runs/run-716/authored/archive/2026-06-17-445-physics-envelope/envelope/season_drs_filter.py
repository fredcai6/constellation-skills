"""Feed the joint-fit CdA_closed + honest σ into the SeasonFilter (#445): a high-σ (poorly-levered)
weekend should self-down-weight and lean on the carried season prior, while a well-levered weekend
moves the estimate. Demonstrates the honest σ closing the loop on the per-weekend + prior middle path.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from season_capability_filter import SeasonFilter  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
drs = json.loads((OUT / "season_drs.json").read_text())

rounds = list(drs.keys())
per_race = [(rn, {t: (v[0], v[3]) for t, v in drs[rn].items()}) for rn in rounds]  # (CdA_c, σ_c)
traj, state, sig2_op, q0 = SeasonFilter().fit(per_race)
print(f"CdA_closed season filter: σ²_op={sig2_op:.3e} (σ_op={np.sqrt(sig2_op):.3f}), q0={q0:.3e}\n")

# Mexico: show raw (high-σ) measurement vs filtered — should be pulled toward prior with little move
print("Mexico City — raw joint CdA_c (σ_c) vs filtered (Kalman gain shrinks the high-σ update):")
print(f"  {'team':>5}{'raw':>8}{'σ_c':>7}{'prior μ':>9}{'filtered μ':>11}{'gain':>7}")
for t in sorted(state):
    tr = traj[t]
    mex = next((row for row in tr if row[0] == "Mexico City"), None)
    if mex is None:
        continue
    i = tr.index(mex)
    key, raw, sg, mu, P, jp = mex
    prior = tr[i - 1][3] if i > 0 else raw
    # implied gain this step
    gain = (mu - prior) / (raw - prior) if abs(raw - prior) > 1e-6 else 0.0
    print(f"  {t:>5}{raw:>8.3f}{sg:>7.3f}{prior:>9.3f}{mu:>11.3f}{gain:>7.2f}")

print("\n(low gain on high-σ Mexico weekends ⇒ filter trusts the season prior there, not the noisy fit)")

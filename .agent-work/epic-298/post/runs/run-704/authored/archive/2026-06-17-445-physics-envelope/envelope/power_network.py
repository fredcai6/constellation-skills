"""Networked per-team POWER rating vs field-mean (#445).

Power is real-but-half-confounded with drag. Two questions:
  1. Does a pairwise NETWORK (robust, σ-weighted, zero-gauge aggregate — not the literal mean) give a
     better per-team power baseline? Edges weighted by 1/(σ_Pi²+σ_Pj²), and σ_P is LARGEST where the
     P↔CdA degeneracy is worst — so the network DOWN-WEIGHTS the most drag-leaked fits. The mean can't.
  2. Does that reduce the power↔drag LEAKAGE vs the field-mean? (corr with the drag rating.)
Also the standard robustness check (corrupt one weekend, who moves).
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

from network_rating import network_solve, build_edges, field_mean  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
drs = json.loads((OUT / "season_drs.json").read_text())
PU = {"MERC": "Merc", "WIL": "Merc", "MCL": "Merc", "AMR": "Merc", "FER": "Fer", "HAA": "Fer",
      "ALF": "Fer", "RBR": "Honda", "ATR": "Honda", "ALP": "Renault"}

# build per-quantity seasons {round: {team: [val, sigma, n]}}
seasonP = {rn: {t: [v[2], v[9], v[6]] for t, v in rec.items()} for rn, rec in drs.items()}      # P, σ_P
seasonD = {rn: {t: [np.log(v[0]), v[3] / v[0], v[6]] for t, v in rec.items()} for rn, rec in drs.items()}  # logCdA
teams = sorted({t for rec in drs.values() for t in rec})

netP, _ = network_solve(build_edges(seasonP), teams)
fmP = field_mean(seasonP)
dragR, _ = network_solve(build_edges(seasonD), teams)

a = np.array([netP[t] for t in teams]); b = np.array([fmP[t] for t in teams])
d = np.array([dragR[t] for t in teams])
leak_net = float(np.corrcoef(a, d)[0, 1]); leak_fm = float(np.corrcoef(b, d)[0, 1])

print("per-team POWER rating: NETWORK (σ-weighted, robust) vs FIELD-MEAN   [field-relative kW]")
print(f"  {'team':>5}{'PU':>8}{'network':>10}{'fieldmean':>11}{'drag(log)':>11}")
for t in sorted(teams, key=lambda k: -netP[k]):
    print(f"  {t:>5}{PU[t]:>8}{netP[t]:>+10.1f}{fmP[t]:>+11.1f}{dragR[t]:>+11.3f}")
print(f"\n  corr(network, fieldmean) = {np.corrcoef(a, b)[0,1]:+.2f}")
print(f"  LEAKAGE corr with drag:  network = {leak_net:+.2f}   field-mean = {leak_fm:+.2f}"
      f"   ({'σ-weighting reduced leakage' if abs(leak_net) < abs(leak_fm) - 0.03 else 'no leakage gain — same confound'})")

# robustness: corrupt one team one weekend (+80 kW), who moves
rn0 = list(seasonP.keys())[10]; victim = "WIL"
if victim in seasonP[rn0]:
    sc = json.loads(json.dumps(seasonP)); sc[rn0][victim][0] += 80.0
    netc, _ = network_solve(build_edges(sc), teams)
    fmc = field_mean(seasonP, override={(rn0, victim): seasonP[rn0][victim][0] + 80.0})
    others = [t for t in teams if t != victim]
    dn = np.mean([abs(netc[t] - netP[t]) for t in others])
    df = np.mean([abs(fmc[t] - fmP[t]) for t in others])
    print(f"\n  ROBUSTNESS — corrupt {victim}@{rn0} by +80 kW. mean |Δ| on OTHER teams:")
    print(f"    network {dn:.2f} kW   field-mean {df:.2f} kW   "
          f"(network shrugs off the bad weekend {dn/max(df,1e-9):.2f}×)")

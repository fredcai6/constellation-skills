"""What the braking frontier gives per team (#445).

A_b = mechanical braking grip (config-INVARIANT per-car; track conditions are common-mode) → global
baseline, season-stable per-car capability. B_b = downforce braking (config-DEPENDENT, wing+density)
→ networked/log-space like CdA. Questions: is each a RESOLVED per-team signal (between/SE)? Is A_b
well-identified or extrapolated (honest σ vs the v→0 lever)? Are A_b and B_b independent (the
intercept↔slope degeneracy)? Is B_b the same axis as drag CdA (aero-platform consolidation)?
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

from network_rating import network_solve, build_edges  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
brk = json.loads((OUT / "season_brake2.json").read_text())   # [A_b,B_b,σA,σB,corrAB,npts,vlo]
drs = json.loads((OUT / "season_drs.json").read_text())      # [CdA_c,...]


def field_rel(season, vidx, sidx, log=False):
    """per team: (round, dev-from-field-median, measurement σ in (log) units)."""
    per = {}
    for rn, rec in season.items():
        vals = {t: (np.log(v[vidx]) if log else v[vidx]) for t, v in rec.items() if v[vidx] > 0}
        if len(vals) < 5:
            continue
        med = np.median(list(vals.values()))
        for t, x in vals.items():
            sg = season[rn][t][sidx] / season[rn][t][vidx] if log else season[rn][t][sidx]
            per.setdefault(t, []).append((rn, x - med, sg))
    return per


def decompose(per, label, unit):
    means, withins, meas = {}, {}, []
    for t, pts in per.items():
        d = np.array([p[1] for p in pts]); s = np.array([p[2] for p in pts])
        w = 1.0 / (s ** 2 + 1e-12)
        mt = np.average(d, weights=w); means[t] = mt
        withins[t] = np.sqrt(np.average((d - mt) ** 2, weights=w)); meas += list(s)
    between = float(np.std(list(means.values()))); within = float(np.median(list(withins.values())))
    msig = float(np.median(meas)); n = float(np.median([len(p) for p in per.values()]))
    se = within / np.sqrt(n)
    print(f"\n=== {label} ===")
    print(f"  between-team σ={between:.3f}{unit}  within(per-track) σ={within:.3f}{unit}  "
          f"measurement σ={msig:.3f}{unit}")
    print(f"  team-mean SE≈{se:.3f}{unit}  between/SE={between/se:.1f} "
          f"({'REAL per-team separation' if between/se > 2 else 'NOT resolved'})  "
          f"discriminability between/within={between/within:.2f}")
    return means


def main():
    # lever / identifiability of A_b
    vlo = np.median([v[6] for rec in brk.values() for v in rec.values()])
    sAr = np.median([v[2] / v[0] for rec in brk.values() for v in rec.values()])
    corrAB = np.median([v[4] for rec in brk.values() for v in rec.values()])
    print(f"A_b identifiability: lowest braking bin median {vlo:.0f} km/h, σ_Ab/A_b median {sAr*100:.1f}%, "
          f"per-fit corr(A_b,B_b) median {corrAB:+.2f}")

    # A_b — mechanical braking grip (config-invariant; field-relative removes track conditions)
    relA = field_rel(brk, 0, 2, log=False)
    mA = decompose(relA, "A_b mechanical braking grip (field-relative, g)", "g")
    # absolute A_b ranking
    absA = {}
    for rn, rec in brk.items():
        for t, v in rec.items():
            absA.setdefault(t, []).append(v[0])
    print("  per-team mechanical braking grip A_b (season median, g):")
    for t in sorted(absA, key=lambda k: -np.median(absA[k])):
        print(f"     {t:>4}  {np.median(absA[t]):.2f}g   (field-rel {mA.get(t, float('nan')):+.3f})")

    # B_b — downforce braking (config-dependent): NETWORK in log-space (density+wing multiplicative)
    relB = field_rel(brk, 1, 3, log=True)
    decompose(relB, "B_b downforce braking (field-relative, log ⇒ fractional)", "")
    seasonB = {rn: {t: [np.log(v[1]), v[3] / v[1], v[5]] for t, v in rec.items() if v[1] > 0}
               for rn, rec in brk.items()}
    teamsB = sorted({t for rec in seasonB.values() for t in rec})
    netB, _ = network_solve(build_edges(seasonB), teamsB)

    # A_b vs B_b independence (cross-team)
    tA = {t: np.median(absA[t]) for t in absA}
    ts = [t for t in tA if t in netB]
    cAB = np.corrcoef([tA[t] for t in ts], [netB[t] for t in ts])[0, 1]
    print(f"\nINDEPENDENCE  corr(A_b mechanical, B_b downforce) across teams = {cAB:+.2f}")

    # B_b downforce-braking vs CdA drag (aero-platform consolidation)
    seasonC = {rn: {t: [np.log(v[0]), v[3] / v[0], v[6]] for t, v in rec.items()} for rn, rec in drs.items()}
    teamsC = sorted({t for rec in seasonC.values() for t in rec})
    netC, _ = network_solve(build_edges(seasonC), teamsC)
    ts2 = [t for t in netB if t in netC]
    cBC = np.corrcoef([netB[t] for t in ts2], [netC[t] for t in ts2])[0, 1]
    print(f"CROSS-AXIS    corr(B_b braking-downforce, CdA drag) network ratings = {cBC:+.2f}  "
          f"({'same aero platform' if abs(cBC) > 0.5 else 'distinct aero axes'})")
    print("\n  per-team B_b downforce-braking network rating (log):")
    for t in sorted(netB, key=lambda k: -netB[k]):
        print(f"     {t:>4}  B_b {netB[t]:+.3f}   CdA {netC.get(t, float('nan')):+.3f}")


if __name__ == "__main__":
    main()

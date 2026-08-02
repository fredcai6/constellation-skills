"""Consolidation (#445): the per-team capability axes built this epic — how independent are they,
and which actually predict quali pace? Spearman across the 10 teams.

Axes:
  apex_pace   cornering pace        apex_feature.apex_speed_q90  (the −0.89-to-pace signal)
  corner_B    cornering downforce   apex_feature.frontier_B
  CdA         drag                  season_drs (network rating, log)
  power       longitudinal (conf.)  season_drs P (field-relative)
  brake_Ab    mechanical braking    season_brake2 A_b (field-relative)
  brake_Bb    downforce braking     season_brake2 B_b (network rating, log)
target: quali_pace (apex_feature; lower = faster).
"""
import json
import sys
from itertools import combinations
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
apex = json.loads((OUT / "apex_feature.json").read_text())
drs = json.loads((OUT / "season_drs.json").read_text())
brk = json.loads((OUT / "season_brake2.json").read_text())


def net_rating(season, vidx, sidx, nidx, log=True):
    sl = {rn: {t: [(np.log(v[vidx]) if log else v[vidx]), v[sidx] / (v[vidx] if log else 1), v[nidx]]
               for t, v in rec.items() if v[vidx] > 0} for rn, rec in season.items()}
    teams = sorted({t for rec in sl.values() for t in rec})
    r, _ = network_solve(build_edges(sl), teams)
    return r


def field_mean_rating(season, vidx, sidx):
    per = {}
    for rn, rec in season.items():
        vals = {t: v[vidx] for t, v in rec.items()}
        med = np.median(list(vals.values()))
        for t, x in vals.items():
            per.setdefault(t, []).append(x - med)
    return {t: float(np.mean(x)) for t, x in per.items()}


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    axes = {
        "apex_pace": apex["apex_speed_q90"],
        "corner_B": apex["frontier_B"],
        "CdA":      net_rating(drs, 0, 3, 6, log=True),
        "power":    field_mean_rating(drs, 2, 9),
        "brake_Ab": field_mean_rating(brk, 0, 2),
        "brake_Bb": net_rating(brk, 1, 3, 5, log=True),
    }
    pace = apex["quali_pace"]
    teams = sorted(set.intersection(*[set(v) for v in axes.values()], set(pace)))
    names = list(axes)
    M = {n: np.array([axes[n][t] for t in teams]) for n in names}
    pc = np.array([pace[t] for t in teams])

    print(f"teams (n={len(teams)}): {teams}\n")
    print("Spearman cross-axis correlation matrix:")
    print("           " + "".join(f"{n:>10}" for n in names))
    for n in names:
        row = "".join(f"{spearman(M[n], M[m]):>10.2f}" for m in names)
        print(f"  {n:>9}{row}")

    print("\nSpearman vs QUALI PACE (|high| = pace-relevant; sign depends on axis orientation):")
    for n in names:
        print(f"  {n:>9}  {spearman(M[n], pc):+.2f}")

    # near-duplicate axes (|r|>0.6) and independent clusters
    print("\nstrongly related axis pairs (|Spearman|>0.6):")
    found = False
    for a, b in combinations(names, 2):
        r = spearman(M[a], M[b])
        if abs(r) > 0.6:
            print(f"  {a} ~ {b}: {r:+.2f}"); found = True
    if not found:
        print("  (none — all axes largely independent)")


if __name__ == "__main__":
    main()

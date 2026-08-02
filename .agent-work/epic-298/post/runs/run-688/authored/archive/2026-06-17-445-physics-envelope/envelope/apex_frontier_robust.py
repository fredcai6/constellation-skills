"""Confirm the HAA tell mechanism: the frontier-B season feature is heavy-tailed
per weekend; MEAN aggregation inflates HAA. Compare MEAN vs MEDIAN aggregation,
and report cross-sectional correlation to quali pace for both.

If median aggregation alone fixes HAA's #1 grip ranking AND improves pace corr,
that's a cheaper fix than apex-speed. If it does NOT (grip-ceiling != pace even
robustly aggregated), that motivates the apex-speed feature.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import aniso_fit  # noqa: E402
from season_prior_filter import fit_weekend, VREF  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
aniso_fit.CACHE = OUT / "calibrated_aniso_nodes.npz"
DRV2TEAM = aniso_fit.DRV2TEAM


def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    return float(np.corrcoef(np.argsort(np.argsort(a)), np.argsort(np.argsort(b)))[0, 1])


def quali_pace_team():
    qp = json.load(open(OUT / "quali_pace_2023.json"))
    acc = {}
    for rnd, teams in qp.items():
        for t, gap in teams.items():
            acc.setdefault(t, []).append(gap)
    return {t: float(np.mean(v)) for t, v in acc.items()}


def main():
    per = aniso_fit.load()
    perweek = {}  # car -> list of B*vref^2
    for rname, cl in per:
        cl_ = aniso_fit.clouds_lat(cl)
        cl_ = {c: v for c, v in cl_.items() if len(v[0]) >= 24}
        if len(cl_) < 4:
            continue
        A, B = fit_weekend(cl_)
        for c in cl_:
            perweek.setdefault(c, []).append(B[c] * VREF * VREF)

    def teamagg(fn):
        teamvals = {}
        for c, vals in perweek.items():
            if len(vals) < 6:
                continue
            t = DRV2TEAM.get(c)
            if t:
                teamvals.setdefault(t, []).append(fn(vals))
        return {t: float(np.mean(v)) for t, v in teamvals.items()}

    qp = quali_pace_team()
    tmean = teamagg(np.mean)
    tmed = teamagg(np.median)
    teams = sorted(set(tmean) & set(qp))

    print("Frontier-B season feature: MEAN vs MEDIAN per-weekend aggregation")
    print(f"{'team':>5} {'B_mean':>8} {'B_med':>8} {'quali':>7}")
    for t in sorted(teams, key=lambda t: -tmean[t]):
        print(f"{t:>5} {tmean[t]:8.3f} {tmed[t]:8.3f} {qp[t]:7.3f}")

    gm = [tmean[t] for t in teams]; gd = [tmed[t] for t in teams]
    g = [qp[t] for t in teams]
    print(f"\n  Spearman(B_mean, quali) = {spearman(gm, g):+.3f}")
    print(f"  Spearman(B_med,  quali) = {spearman(gd, g):+.3f}")
    print("  (want negative: more grip -> lower gap -> faster)")

    rmean = sorted(teams, key=lambda t: -tmean[t])
    rmed = sorted(teams, key=lambda t: -tmed[t])
    print(f"\n  grip rank (MEAN): {rmean}")
    print(f"  grip rank (MED):  {rmed}")
    print(f"  HAA: mean-rank #{rmean.index('HAA')+1}, median-rank #{rmed.index('HAA')+1}")

    # how heavy-tailed is each team's per-weekend B?
    print("\n  per-weekend B*vref^2 tail (max / median ratio):")
    for t in sorted(teams):
        drvs = [c for c in perweek if DRV2TEAM.get(c) == t]
        vals = np.concatenate([perweek[c] for c in drvs])
        print(f"    {t:>4}: median {np.median(vals):.2f}  max {vals.max():.2f}  "
              f"ratio {vals.max()/np.median(vals):.1f}x")


if __name__ == "__main__":
    main()

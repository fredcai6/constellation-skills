"""Baseline: reproduce the frontier-g B (downforce/grip-ceiling) season feature and
its cross-sectional correlation to quali pace — the thing apex-speed must beat.

This is the LATERAL-apex frontier (the adopted grip observable): per weekend a
shared mechanical intercept A + per-car downforce slope B on v^2, fit on near-apex
pure-lateral nodes. Season feature = mean over rounds of B*VREF^2 (grip g at vref).

Confirms the established HAA paradox: HAA reads high cornering grip but is slow.
Reports cross-sectional Spearman & Pearson vs quali pace at TEAM level.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import aniso_fit  # noqa: E402
from season_prior_filter import fit_weekend, VREF, GSAT  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
aniso_fit.CACHE = OUT / "calibrated_aniso_nodes.npz"
DRV2TEAM = aniso_fit.DRV2TEAM

# round-name -> round-number (quali_pace_2023.json keys)
ROUND_NUM = {
    "Bahrain": 1, "Saudi Arabian": 2, "Australian": 3, "Azerbaijan": 4, "Miami": 5,
    "Monaco": 6, "Spanish": 7, "Canadian": 8, "Austrian": 9, "British": 10,
    "Hungarian": 11, "Belgian": 12, "Dutch": 13, "Italian": 14, "Singapore": 15,
    "Japanese": 16, "Qatar": 17, "United States": 18, "Mexico City": 19,
    "São Paulo": 20, "Las Vegas": 21, "Abu Dhabi": 22,
}


def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def pearson(a, b):
    return float(np.corrcoef(a, b)[0, 1])


def season_frontier_B():
    """Per-car season-mean grip g at vref (lateral-apex frontier)."""
    per = aniso_fit.load()
    seasonB = {}
    for rname, cl in per:
        cl_ = aniso_fit.clouds_lat(cl)  # near-apex pure-lateral
        cl_ = {c: v for c, v in cl_.items() if len(v[0]) >= 24}
        if len(cl_) < 4:
            continue
        A, B = fit_weekend(cl_)
        for c in cl_:
            seasonB.setdefault(c, []).append(B[c] * VREF * VREF)
    return {c: float(np.mean(v)) for c, v in seasonB.items() if len(v) >= 6}


def quali_pace_team():
    """Season-mean quali gap-to-median per team (negative = faster)."""
    qp = json.load(open(OUT / "quali_pace_2023.json"))
    acc = {}
    for rnd, teams in qp.items():
        for t, gap in teams.items():
            acc.setdefault(t, []).append(gap)
    return {t: float(np.mean(v)) for t, v in acc.items()}


def main():
    carB = season_frontier_B()
    # team-aggregate
    teamB = {}
    for c, b in carB.items():
        t = DRV2TEAM.get(c)
        if t:
            teamB.setdefault(t, []).append(b)
    teamB = {t: float(np.mean(v)) for t, v in teamB.items()}

    qp = quali_pace_team()
    teams = sorted(set(teamB) & set(qp), key=lambda t: -teamB[t])

    print("=" * 70)
    print("FRONTIER-G (lateral-apex downforce B) season feature vs QUALI PACE")
    print("=" * 70)
    print(f"{'team':>5} {'gripG':>8} {'quali_gap':>10}  (gap<0 = faster)")
    for t in teams:
        print(f"{t:>5} {teamB[t]:8.3f} {qp[t]:10.3f}")

    gb = np.array([teamB[t] for t in teams])
    gp = np.array([qp[t] for t in teams])
    # quali: lower (more negative) = faster. grip: higher = more grip.
    # If grip => pace, higher grip should pair with LOWER gap => negative corr.
    print(f"\n  cross-sectional Spearman(gripG, quali_gap) = {spearman(gb, gp):+.3f}")
    print(f"  cross-sectional Pearson (gripG, quali_gap) = {pearson(gb, gp):+.3f}")
    print("  (want NEGATIVE: more grip -> faster -> lower gap)")

    # HAA tell
    rankB = sorted(teams, key=lambda t: -teamB[t])
    rankP = sorted(teams, key=lambda t: qp[t])
    print(f"\n  grip ranking (most->least): {rankB}")
    print(f"  pace ranking (fast->slow):  {rankP}")
    if "HAA" in teamB:
        print(f"\n  HAA grip rank #{rankB.index('HAA')+1}/{len(teams)}  "
              f"(gripG={teamB['HAA']:.3f})")
        print(f"  HAA pace rank #{rankP.index('HAA')+1}/{len(teams)}  "
              f"(quali_gap={qp['HAA']:+.3f})")

    json.dump({"teamB": teamB, "quali_pace": qp, "carB": carB},
              open(OUT / "apex_baseline_frontier.json", "w"), indent=2)
    print(f"\nwrote apex_baseline_frontier.json")


if __name__ == "__main__":
    main()

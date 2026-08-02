"""Apex-speed / corner-time per-car SEASON FEATURE + pace-relevance comparison (#445).

Reads apex_corners.npz (clean per-corner records). Builds two candidate features and
tests whether either is MORE pace-relevant than the frontier-g B:

FEATURE A — apex-speed-at-matched-radius (geometry-normalized cornering speed):
  Per car-weekend, the corner's apex speed depends on the car AND the corner radius R.
  Physics at the limit: v_apex = sqrt(a_lat * R)  ->  log v_apex = 0.5 log R + 0.5 log a_lat.
  Fit a SHARED slope on log R + a PER-CAR offset within each weekend (the field shares the
  same set of corners that weekend; the offset is the car's apex-speed-at-radius capability).
  Equivalently: a per-car shift in log v_apex after removing the corner-radius (track) effect.
  Season feature = mean of per-weekend offsets. Higher = faster through corners of a
  given radius = more pace-relevant cornering.

  Robust variant: use the UPPER edge (the car was on the limit on its best lap), via a
  high quantile of the per-corner offset within the weekend.

FEATURE B — corner-traversal time (geometry-normalized):
  corner_dt is how long the car spends in the corner. Normalized by corner arc length
  (corner_ds) -> mean inverse speed through the corner. Lower (faster) = better. Same
  per-weekend shared-geometry + per-car offset removal.

Cross-sectional test at TEAM level vs quali pace (Spearman + Pearson). Does apex-speed
track pace better than frontier-g, and does HAA read appropriately SLOW?
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
NPZ = OUT / "apex_corners.npz"
DRV2TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "LEC": "FER",
            "SAI": "FER", "NOR": "MCL", "PIA": "MCL", "ALO": "AMR", "STR": "AMR",
            "GAS": "ALP", "OCO": "ALP", "ALB": "WIL", "SAR": "WIL", "TSU": "ATR",
            "DEV": "ATR", "RIC": "ATR", "LAW": "ATR", "BOT": "ALF", "ZHO": "ALF",
            "MAG": "HAA", "HUL": "HAA"}
MIN_CORNERS = 10       # per car-weekend to estimate an offset
MIN_WEEKENDS = 6       # per car to enter the season feature


def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    return float(np.corrcoef(np.argsort(np.argsort(a)), np.argsort(np.argsort(b)))[0, 1])


def pearson(a, b):
    return float(np.corrcoef(a, b)[0, 1])


def load():
    d = np.load(NPZ, allow_pickle=True)
    return {k: d[k] for k in d.files}


def quali_pace_team():
    qp = json.load(open(OUT / "quali_pace_2023.json"))
    acc = {}
    for rnd, teams in qp.items():
        for t, gap in teams.items():
            acc.setdefault(t, []).append(gap)
    return {t: float(np.mean(v)) for t, v in acc.items()}


def weekend_offsets(rnd_mask, d, ycol, geomcol, use_quantile=None):
    """Within one weekend, remove the shared corner-geometry effect and return per-car
    offsets. Model:  y = beta*log(geom) + sum_car alpha_car * 1[car] + eps.
    Returns {car: offset}. If use_quantile, take that quantile of per-corner residual
    (car on the limit) instead of the mean offset.
    """
    car = d["car"][rnd_mask]
    y = ycol[rnd_mask]
    g = geomcol[rnd_mask]
    ok = np.isfinite(y) & np.isfinite(g) & (g > 0) & (y > 0)
    car, y, g = car[ok], y[ok], g[ok]
    cars = sorted(set(car))
    cars = [c for c in cars if (car == c).sum() >= MIN_CORNERS]
    if len(cars) < 4:
        return {}
    m = np.isin(car, cars)
    car, y, g = car[m], y[m], g[m]
    logy = np.log(y); logg = np.log(g)
    # design: log(geom) + per-car dummies (no global intercept; absorbed by dummies)
    cidx = {c: j for j, c in enumerate(cars)}
    X = np.zeros((len(y), 1 + len(cars)))
    X[:, 0] = logg
    for j, c in enumerate(cars):
        X[car == c, 1 + j] = 1.0
    coef, *_ = np.linalg.lstsq(X, logy, rcond=None)
    beta = coef[0]
    alpha = {c: coef[1 + cidx[c]] for c in cars}
    if use_quantile is not None:
        # per-car quantile of (logy - beta*logg) = on-limit offset
        resid = logy - beta * logg
        alpha = {c: float(np.quantile(resid[car == c], use_quantile)) for c in cars}
    # center offsets to zero mean across cars (remove weekend grip level -> car-relative)
    mu = np.mean(list(alpha.values()))
    return {c: alpha[c] - mu for c in alpha}


def season_feature(d, ycol, geomcol, use_quantile=None):
    rounds = list(d["rounds"])
    percar = {}
    for rnd in rounds:
        mask = d["round"] == rnd
        if mask.sum() < 4 * MIN_CORNERS:
            continue
        offs = weekend_offsets(mask, d, ycol, geomcol, use_quantile=use_quantile)
        for c, o in offs.items():
            percar.setdefault(c, []).append(o)
    return {c: float(np.median(v)) for c, v in percar.items() if len(v) >= MIN_WEEKENDS}


def team_agg(carfeat):
    t = {}
    for c, v in carfeat.items():
        tm = DRV2TEAM.get(c)
        if tm:
            t.setdefault(tm, []).append(v)
    return {tm: float(np.mean(v)) for tm, v in t.items()}


def report(name, teamfeat, qp, higher_is_faster):
    teams = sorted(set(teamfeat) & set(qp))
    f = np.array([teamfeat[t] for t in teams])
    g = np.array([qp[t] for t in teams])
    # quali gap: lower = faster. feature: if higher_is_faster, want NEGATIVE corr.
    sp = spearman(f, g); pe = pearson(f, g)
    sign = "" if higher_is_faster else " (sign flipped: lower feat = faster)"
    print(f"\n=== {name}{sign} ===")
    order = sorted(teams, key=(lambda t: -teamfeat[t]) if higher_is_faster else (lambda t: teamfeat[t]))
    print(f"  {'team':>5} {'feat':>9} {'quali':>8}")
    for t in order:
        print(f"  {t:>5} {teamfeat[t]:9.4f} {qp[t]:8.3f}")
    print(f"  Spearman(feat, quali) = {sp:+.3f}   Pearson = {pe:+.3f}")
    want = "NEGATIVE" if higher_is_faster else "POSITIVE"
    print(f"  (pace-relevant if {want}: capability pairs with low gap)")
    rk = order  # already fast->slow by feature
    pacerank = sorted(teams, key=lambda t: qp[t])
    if "HAA" in teamfeat:
        print(f"  HAA feature-rank #{rk.index('HAA')+1}/{len(teams)}  "
              f"pace-rank #{pacerank.index('HAA')+1}/{len(teams)}")
    return sp, pe


def main():
    d = load()
    n = len(d["v_apex"])
    print(f"loaded {n} corner-records, {len(set(zip(d['round'], d['car'])))} car-weekends, "
          f"{len(d['rounds'])} rounds")
    qp = quali_pace_team()

    vapex = d["v_apex"].astype(float)
    Rapex = d["R_apex"].astype(float)
    cdt = d["corner_dt"].astype(float)
    cds = d["corner_ds"].astype(float)
    # mean inverse speed through corner (s/m): higher = slower
    inv_speed = np.where((cds > 0) & (cdt > 0), cdt / cds, np.nan)

    # FEATURE A: apex-speed at matched radius (mean offset)
    fA = season_feature(d, vapex, Rapex, use_quantile=None)
    tA = team_agg(fA)
    spA, peA = report("FEATURE A: apex-speed @ matched radius (mean offset)", tA, qp, True)

    # FEATURE A': on-limit upper quantile (best-lap apex)
    fAq = season_feature(d, vapex, Rapex, use_quantile=0.90)
    tAq = team_agg(fAq)
    spAq, peAq = report("FEATURE A': apex-speed @ radius, 90th-pct on-limit offset", tAq, qp, True)

    # FEATURE B: corner-traversal inverse-speed normalized (use corner_ds as geom)
    # model log(inv_speed) ~ log(corner_ds)+per-car ; lower inv_speed = faster
    fB = season_feature(d, inv_speed, cds, use_quantile=None)
    tB = team_agg(fB)
    spB, peB = report("FEATURE B: corner-traversal inverse-speed (lower=faster)", tB, qp, False)

    # Baseline frontier for side-by-side
    base = json.load(open(OUT / "apex_baseline_frontier.json"))
    tF = base["teamB"]
    spF, peF = report("BASELINE: frontier-g B (mean aggregation)", tF, qp, True)

    print("\n" + "=" * 66)
    print("PACE-RELEVANCE SUMMARY (|Spearman| to quali pace, higher=better)")
    print("=" * 66)
    print(f"  frontier-g B (mean):          Spearman {spF:+.3f}  Pearson {peF:+.3f}")
    print(f"  apex-speed @ radius (mean):   Spearman {spA:+.3f}  Pearson {peA:+.3f}")
    print(f"  apex-speed @ radius (90th):   Spearman {spAq:+.3f}  Pearson {peAq:+.3f}")
    print(f"  corner inverse-speed:         Spearman {spB:+.3f}  Pearson {peB:+.3f}")

    json.dump({
        "apex_speed_mean": tA, "apex_speed_q90": tAq, "corner_invspeed": tB,
        "frontier_B": tF, "quali_pace": qp,
        "corr": {"frontier_sp": spF, "apexmean_sp": spA, "apexq90_sp": spAq,
                 "invspeed_sp": spB}}, open(OUT / "apex_feature.json", "w"), indent=2)
    print("\nwrote apex_feature.json")


if __name__ == "__main__":
    main()

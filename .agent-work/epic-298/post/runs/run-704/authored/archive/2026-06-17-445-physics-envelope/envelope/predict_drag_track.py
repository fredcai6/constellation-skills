"""NORTH STAR test #1: does aero CHARACTER predict track-specific performance? (#445)

The evo predictor's weakness: dominated by previous weekends, blind to current-
weekend capability transfer. The drag fingerprint should fix exactly that: a slippery
(low-drag) car over-performs its own season average at LOW-downforce tracks (top speed
matters) and under-performs at HIGH-downforce tracks. If the season drag character
predicts each car's per-track over/under-performance OUT OF SAMPLE, that's the
capability-transfer signal recency can't give.

Target  : residual pace = team's quali gap-to-field at race T  minus  team's season
          mean gap (its track-specific over/under-performance, + = slower than usual).
Track   : field-mean CdA at race T (high = high-downforce track) — derived from the
          drag fits themselves.
Feature : team season drag offset (− = slippery) × track axis.
Eval    : leave-one-RACE-out; predicted vs actual residual rank-corr on held-out race.
"""
from __future__ import annotations

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

import harvest_envelope as H  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
DRAGFITS = OUT / "drag_fingerprint10_fits.json"
PACE = OUT / "quali_pace_2023.json"

TEAMMAP = {  # FastF1 Team string -> short code
    "Red Bull Racing": "RBR", "Mercedes": "MERC", "Ferrari": "FER", "McLaren": "MCL",
    "Aston Martin": "AMR", "Alpine": "ALP", "Williams": "WIL", "AlphaTauri": "ATR",
    "Alfa Romeo": "ALF", "Haas F1 Team": "HAA",
}


def collect_pace():
    if PACE.exists():
        return {int(k): v for k, v in json.loads(PACE.read_text()).items()}
    out = {}
    for rd in range(1, 23):
        try:
            q = H.load_session(2023, rd, "Q")
        except Exception:
            continue
        laps = q.laps
        laps = laps[laps["LapTime"].notna()]
        best = {}
        for _, r in laps.iterrows():
            team = TEAMMAP.get(str(r["Team"]))
            if team is None:
                continue
            t = r["LapTime"].total_seconds()
            if team not in best or t < best[team]:
                best[team] = float(t)
        if len(best) >= 8:
            med = float(np.median(list(best.values())))
            out[rd] = {t: best[t] - med for t in best}     # gap to field median (s)
        print(f"  round {rd:>2}: {len(best)} teams paced", flush=True)
    PACE.write_text(json.dumps(out, indent=1))
    return out


def main():
    fits = {int(k): v for k, v in json.loads(DRAGFITS.read_text()).items()}
    pace = collect_pace()
    rounds = sorted(set(fits) & set(pace))

    # track axis = field-mean CdA per race (high = high-downforce track)
    fieldCdA = {rd: np.mean([fits[rd][t]["CdA_c"] for t in fits[rd]]) for rd in rounds}
    cda_mean = np.mean(list(fieldCdA.values()))
    track_axis = {rd: fieldCdA[rd] - cda_mean for rd in rounds}

    # season drag offset per team (− = slippery), from per-race relative CdA
    teams = sorted({t for rd in rounds for t in fits[rd]})
    drag_off = {}
    for t in teams:
        vals = [fits[rd][t]["CdA_c"] - fieldCdA[rd] for rd in rounds if t in fits[rd]]
        if len(vals) >= 6:
            drag_off[t] = float(np.mean(vals))

    # residual pace per (team, race) = gap minus team season-mean gap
    gap = {t: {rd: pace[rd][t] for rd in rounds if t in pace[rd]} for t in teams}
    resid = {}
    for t in teams:
        if t not in drag_off or len(gap[t]) < 6:
            continue
        mu = np.mean(list(gap[t].values()))
        resid[t] = {rd: gap[t][rd] - mu for rd in gap[t]}

    # ---- build the design: y = residual, x = drag_off[t] * track_axis[rd] ----
    rows = []
    for t in resid:
        for rd in resid[t]:
            rows.append((t, rd, resid[t][rd], drag_off[t] * track_axis[rd]))
    y = np.array([r[2] for r in rows]); x = np.array([r[3] for r in rows])
    beta = np.sum(x * y) / np.sum(x * x)
    pred = beta * x
    ss_res = np.sum((y - pred) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot
    corr = np.corrcoef(x, y)[0, 1]

    print("\n" + "=" * 72)
    print("AERO-CHARACTER → TRACK-SPECIFIC PERFORMANCE  (drag × track interaction)")
    print("=" * 72)
    print(f"  n = {len(rows)} (team,race) points; {len(resid)} teams x {len(rounds)} races")
    print(f"  interaction slope β = {beta:+.3f}  (expect NEGATIVE: slippery car [drag_off<0]")
    print(f"    at low-DF track [axis<0] -> product>0 -> FASTER -> residual<0)")
    print(f"  in-sample corr(x,y) = {corr:+.3f}   R² = {r2:+.3f}")

    # ---- leave-one-RACE-out: predict held-out race residuals, rank-corr ----
    def spear(a, b):
        ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
        return np.corrcoef(ra, rb)[0, 1] if len(a) > 2 else np.nan
    loo = []
    for hr in rounds:
        tr = [r for r in rows if r[1] != hr]
        te = [r for r in rows if r[1] == hr]
        if len(te) < 4:
            continue
        xtr = np.array([r[3] for r in tr]); ytr = np.array([r[2] for r in tr])
        b = np.sum(xtr * ytr) / np.sum(xtr * xtr)
        xte = np.array([r[3] for r in te]); yte = np.array([r[2] for r in te])
        s = spear(b * xte, yte)
        if not np.isnan(s):
            loo.append(s)
    print(f"\n  leave-one-race-out predicted-vs-actual rank corr: "
          f"mean {np.mean(loo):+.3f} (median {np.median(loo):+.3f}, "
          f"{np.mean(np.array(loo) > 0)*100:.0f}% of races positive, n={len(loo)})")

    # ---- per-team track sensitivity vs slipperiness (interpretable view) ----
    print("\n" + "-" * 72)
    print("per-team: slope of residual vs track-DF-axis  (− = over-performs at high-DF;")
    print("+ = over-performs at LOW-DF i.e. slippery-car signature). sorted by drag_off")
    print(f"{'team':>5} {'drag_off':>9} {'track-slope':>12} {'known':>22}")
    KNOWN = {"AMR": "draggy hi-DF", "MERC": "draggy", "HAA": "draggy mid",
             "MCL": "mixed(upgrade)", "FER": "powerful", "WIL": "slippery!",
             "RBR": "efficient", "ALF": "ferrari pwr", "ATR": "mid", "ALP": "renault"}
    for t in sorted(resid, key=lambda k: drag_off[k]):
        rds = [rd for rd in resid[t]]
        xt = np.array([track_axis[rd] for rd in rds])
        yt = np.array([resid[t][rd] for rd in rds])
        slope = np.sum((xt - xt.mean()) * (yt - yt.mean())) / np.sum((xt - xt.mean())**2)
        print(f"{t:>5} {drag_off[t]:+9.3f} {slope:+12.2f} {KNOWN.get(t,''):>22}")
    print("\n(slippery cars [drag_off<0] should show POSITIVE track-slope: faster than")
    print(" their average at low-DF tracks. corr(drag_off, slope) across teams:)")
    do = np.array([drag_off[t] for t in resid]); sl = np.array([
        np.sum((np.array([track_axis[rd] for rd in resid[t]]) - np.mean([track_axis[rd] for rd in resid[t]])) *
               (np.array([resid[t][rd] for rd in resid[t]]) - np.mean(list(resid[t].values())))) /
        np.sum((np.array([track_axis[rd] for rd in resid[t]]) - np.mean([track_axis[rd] for rd in resid[t]]))**2)
        for t in resid])
    print(f"  corr(drag_off, track-slope) = {np.corrcoef(do, sl)[0,1]:+.3f}  "
          f"(expect NEGATIVE: low drag_off -> high positive slope)")


if __name__ == "__main__":
    main()

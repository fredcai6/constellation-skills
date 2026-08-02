"""NORTH STAR test #3: does physics ADD to a pace baseline? (the fair test, #445)

Physics shouldn't have to BEAT recent pace (which already integrates everything) — the
fair question is whether the aero fingerprint explains the part of next-race pace that
recency MISSES: the track-specific deviation. So:
  baseline  = season-avg pace through race n-1 (strong persistent predictor)
  +physics  = baseline + β·(df_off × track-DF-axis)   [β trained on past races only]
Does adding physics improve the leave-FUTURE-out prediction of race n's order?
If even this gives nothing, physics is for CHARACTER, not prediction — full stop.
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

from season_prior_filter import fit_weekend, VREF  # noqa: E402
from predict_grip_track import load_full, constructor_offsets, kfilter, DRV2TEAM, spear  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
PACE = OUT / "quali_pace_2023.json"
DRAGFITS = OUT / "drag_fingerprint10_fits.json"


def main():
    seq = constructor_offsets(load_full())
    pace = {int(k): v for k, v in json.loads(PACE.read_text()).items()}
    pace_by_round = [pace[r] for r in sorted(pace)]
    dragfits = {int(k): v for k, v in json.loads(DRAGFITS.read_text()).items()}
    dr = sorted(dragfits)
    # drag offset per team per race (relative CdA) + season drag offset
    fieldCdA = {i: np.mean([dragfits[rd][t]["CdA_c"] for t in dragfits[rd]])
                for i, rd in enumerate(dr)}
    dragoff_season = {}
    for t in set(t for rd in dragfits for t in dragfits[rd]):
        v = [dragfits[rd][t]["CdA_c"] - fieldCdA[i] for i, rd in enumerate(dr) if t in dragfits[rd]]
        if len(v) >= 6:
            dragoff_season[t] = float(np.mean(v))

    fieldDF = [s["fieldDF"] for s in seq]
    dfmean = np.mean(fieldDF)
    N = min(len(seq), len(pace_by_round))

    base_s, comb_s, dragcomb_s = [], [], []
    for n in range(5, N):
        prN = pace_by_round[n]
        # season-avg pace baseline through n-1
        savg = {}
        for t in prN:
            vals = [pace_by_round[k][t] for k in range(n) if t in pace_by_round[k]]
            if vals:
                savg[t] = np.mean(vals)
        # causal grip downforce offset through n-1
        _, st = kfilter(seq[:n])
        dfoff = {t: st[t][0] for t in st}
        # train interaction β on past races (residual-from-savg ~ dfoff*axis)
        xs, ys = [], []
        for k in range(5, n):
            prk = pace_by_round[k]
            for t in prk:
                sv = [pace_by_round[j][t] for j in range(k) if t in pace_by_round[j]]
                if not sv or t not in dfoff:
                    continue
                ys.append(prk[t] - np.mean(sv))
                xs.append(dfoff[t] * (fieldDF[k] - dfmean))
        if len(xs) > 20 and np.sum(np.array(xs)**2) > 0:
            beta = np.sum(np.array(xs)*np.array(ys)) / np.sum(np.array(xs)**2)
        else:
            beta = 0.0
        # drag interaction β too
        xsd, ysd = [], []
        for k in range(5, n):
            prk = pace_by_round[k]
            for t in prk:
                sv = [pace_by_round[j][t] for j in range(k) if t in pace_by_round[j]]
                if not sv or t not in dragoff_season:
                    continue
                ysd.append(prk[t] - np.mean(sv))
                xsd.append(dragoff_season[t] * (fieldCdA[k] - np.mean(list(fieldCdA.values()))))
        betad = (np.sum(np.array(xsd)*np.array(ysd)) / np.sum(np.array(xsd)**2)
                 if len(xsd) > 20 and np.sum(np.array(xsd)**2) > 0 else 0.0)

        tgt = [t for t in prN if t in savg]
        if len(tgt) < 5:
            continue
        actual = np.array([prN[t] for t in tgt])
        base = np.array([savg[t] for t in tgt])
        phys = np.array([beta * dfoff.get(t, 0.0) * (fieldDF[n] - dfmean) for t in tgt])
        physd = np.array([betad * dragoff_season.get(t, 0.0) *
                          (fieldCdA[n] - np.mean(list(fieldCdA.values()))) for t in tgt])
        # rank-corr: predict order (smaller gap = faster). use -pred vs -actual
        base_s.append(spear(-base, -actual))
        comb_s.append(spear(-(base + phys), -actual))
        dragcomb_s.append(spear(-(base + phys + physd), -actual))

    print("=" * 72)
    print("FAIR TEST: does physics ADD to a season-avg pace baseline? (leave-future-out)")
    print("=" * 72)
    print(f"  baseline (season-avg pace)        : {np.nanmean(base_s):+.4f}")
    print(f"  + grip interaction                : {np.nanmean(comb_s):+.4f}  "
          f"(Δ {np.nanmean(comb_s)-np.nanmean(base_s):+.4f})")
    print(f"  + grip + drag interaction         : {np.nanmean(dragcomb_s):+.4f}  "
          f"(Δ {np.nanmean(dragcomb_s)-np.nanmean(base_s):+.4f})")
    print(f"  n = {len(base_s)} predicted races")
    print("\n  per-race: physics improved the prediction in "
          f"{np.mean(np.array(comb_s) > np.array(base_s))*100:.0f}% of races (grip), "
          f"{np.mean(np.array(dragcomb_s) > np.array(base_s))*100:.0f}% (grip+drag)")
    print("\n  VERDICT: if Δ≈0 and ~50% win rate, physics adds nothing predictive over")
    print("  recent pace — the fingerprint is for CHARACTER, not forecasting.")


if __name__ == "__main__":
    main()

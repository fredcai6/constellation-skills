"""Candidate-selection evidence for issue #387 D3.3 (NOT a deliverable).

Scores the two race observables from src.evo_predictor.race_pace_gap over real races:
  PRIMARY  = integrated_pace_gap (green-flag per-lap pace delta, averaged)
  BASELINE = finishing_gap (total-time gap to field median)

Two criteria the ruling demands:
  (a) DISCRIMINATING POWER between blowout and packed events:
      cross-event CV of per-event gap dispersion. A good observable makes events
      DISTINGUISHABLE (high CV across events) — the whole reason option 2 exists is
      that the retro labels have CV ~0.001 (FINDING.md). Higher = better separation.
  (b) ROBUSTNESS on late-caution races:
      late cautions bunch the field -> the finishing gap COMPRESSES (drivers cross the
      line nose-to-tail behind the SC) while green-lap pace is unaffected. For races with
      a high caution-lap fraction we compare each candidate's dispersion to the same
      race's GREEN-ONLY integrated dispersion (the caution-free pace truth). The candidate
      whose dispersion tracks green pace better on caution races is more robust.

Reads DB only via get_race_lap_times. CPU only. Prints a compact table + verdict inputs.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from statistics import median
from typing import Dict, List, Tuple

import pandas as pd

from src.evo_predictor.race_pace_gap import (
    field_median_spike_actionable_mask,
    finishing_gap,
    gap_dispersion,
    green_actionable_lap_numbers,
    integrated_pace_gap,
    lap_rows_from_frame,
)

DATA = Path("data")
YEARS = (2022, 2023, 2024)


def race_frame(con: sqlite3.Connection, rnd: int) -> pd.DataFrame:
    q = """
      SELECT lt.driver_id, lt.lap_number, lt.lap_time, lt.track_status,
             lt.valid_lap, lt.pit_in_time, lt.pit_out_time
      FROM lap_times lt JOIN sessions s ON lt.session_id=s.id
      WHERE s.round_num=? AND s.session_type='R'
      ORDER BY lt.lap_number, lt.driver_id
    """
    return pd.read_sql_query(q, con, params=(rnd,))


def caution_fraction(rows) -> float:
    laps = {r.lap_number for r in rows if r.lap_number is not None}
    green = green_actionable_lap_numbers(rows)
    if not laps:
        return 0.0
    return 1.0 - len(green) / len(laps)


def cv(values: List[float]) -> float:
    vals = [v for v in values if v == v and v is not None]
    if len(vals) < 2:
        return float("nan")
    m = sum(vals) / len(vals)
    if m == 0:
        return float("nan")
    sd = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5
    return sd / m


def main() -> None:
    prim_disp: List[float] = []
    base_disp: List[float] = []
    rows_for_caution: List[Tuple[str, float, float, float, float]] = []
    labelled: List[Tuple[str, float, float]] = []

    for yr in YEARS:
        dbp = DATA / f"f1_data_{yr}.db"
        if not dbp.exists():
            continue
        con = sqlite3.connect(str(dbp))
        cur = con.cursor()
        cur.execute("SELECT DISTINCT round_num FROM sessions WHERE session_type='R' ORDER BY round_num")
        rounds = [r[0] for r in cur.fetchall()]
        for rnd in rounds:
            df = race_frame(con, rnd)
            if df.empty:
                continue
            rows = lap_rows_from_frame(df)
            prim = integrated_pace_gap(rows)
            base = finishing_gap(rows)
            dp = gap_dispersion(prim)
            db_ = gap_dispersion(base)
            if dp > 0:
                prim_disp.append(dp)
            if db_ > 0:
                base_disp.append(db_)
            cf = caution_fraction(rows)
            labelled.append((f"{yr}R{rnd}", dp, db_))
            # green-only dispersion is the same integrated_pace_gap (it already restricts
            # to green); for the caution-robustness test compare BASELINE vs PRIMARY on
            # high-caution races: how much does each deviate from a low-caution norm?
            rows_for_caution.append((f"{yr}R{rnd}", cf, dp, db_, len(prim)))
        con.close()

    print("==== (a) DISCRIMINATING POWER: cross-event CV of per-event dispersion ====")
    print(f"  PRIMARY  (integrated green pace): n={len(prim_disp)} "
          f"mean_disp={sum(prim_disp)/len(prim_disp):.5f} CV={cv(prim_disp):.4f}")
    print(f"  BASELINE (finishing gap):        n={len(base_disp)} "
          f"mean_disp={sum(base_disp)/len(base_disp):.5f} CV={cv(base_disp):.4f}")
    print("  (higher CV = events more distinguishable = better spread target signal)")

    # Blowout vs packed exemplars by PRIMARY dispersion
    labelled_sorted = sorted([x for x in labelled if x[1] > 0], key=lambda t: t[1])
    print("\n==== blowout vs packed exemplars (by PRIMARY dispersion) ====")
    print("  most PACKED (smallest spread):")
    for name, dp, db_ in labelled_sorted[:4]:
        print(f"    {name:>8}  primary_disp={dp:.5f}  baseline_disp={db_:.5f}")
    print("  most BLOWOUT (largest spread):")
    for name, dp, db_ in labelled_sorted[-4:]:
        print(f"    {name:>8}  primary_disp={dp:.5f}  baseline_disp={db_:.5f}")

    print("\n==== (b) ROBUSTNESS: high-caution races (caution_frac >= 0.20) ====")
    hi = sorted([r for r in rows_for_caution if r[1] >= 0.20], key=lambda t: -t[1])
    print(f"  {'event':>8} {'caut_frac':>9} {'primary':>9} {'baseline':>9}  base/prim ratio")
    ratios: List[float] = []
    for name, cf, dp, db_, _n in hi[:12]:
        ratio = (db_ / dp) if dp > 0 else float("nan")
        if ratio == ratio:
            ratios.append(ratio)
        print(f"  {name:>8} {cf:>9.2f} {dp:>9.5f} {db_:>9.5f}  {ratio:>6.2f}")
    # On caution races, does baseline collapse (ratio<1) relative to green pace?
    lowcaut = [r for r in rows_for_caution if r[1] < 0.10 and r[2] > 0]
    lc_ratios = [(r[3] / r[2]) for r in lowcaut if r[2] > 0]
    print(f"\n  median base/prim dispersion ratio  high-caution(>=0.20): "
          f"{median(ratios) if ratios else float('nan'):.3f}  (n={len(ratios)})")
    print(f"  median base/prim dispersion ratio  low-caution (<0.10): "
          f"{median(lc_ratios) if lc_ratios else float('nan'):.3f}  (n={len(lc_ratios)})")
    print("  (if baseline ratio DROPS on high-caution vs low-caution races, the finishing")
    print("   gap is being compressed by cautions -> PRIMARY is the robust choice)")


if __name__ == "__main__":
    main()

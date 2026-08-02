"""x4 excursion: absolute vs weekend-relative normalization stability probe.

Read-only against data/physics_estimates.db:session_estimates. For each of the
five-view physical axes, compares two normalization schemes:

  (a) absolute  - raw physical-unit estimate per (year, gp_name, constructor)
  (b) relative  - car value minus that weekend's field MEDIAN across
                  constructors (year, round_idx), status='ok' only

For each scheme we estimate:
  - field_sigma: typical within-weekend spread across constructors (this is
    scheme-invariant by construction -- subtracting a per-weekend constant
    does not change the spread WITHIN that weekend -- but we compute it under
    both to sanity check the two numbers agree).
  - noise_sd: typical weekend-to-weekend spread for the SAME car (year,
    constructor) around its own season mean -- i.e. how much a single
    weekend's reading jitters around what that car "really" is.
  - N_weekends = (noise_sd / field_sigma)^2 -- weekends of averaging needed
    to resolve a difference of one field-sigma at 1 SE, sigma/sqrt(N) logic.

Aggregation: per (year, constructor) car-season with >= MIN_WEEKENDS ok rows,
compute that car-season's own-mean residual SD across weekends. Pool car-
season SDs via median (robust to the occasional wild car-season). Field sigma
is the median across (year, round_idx) weekends of the cross-constructor SD
(weekends with >= MIN_FIELD constructors only).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

DB = Path(__file__).resolve().parents[4] / "data" / "physics_estimates.db"

AXES = [
    "drag_area_closed_m2",
    "brake_decel_ms2",
    "brake_aero_decel_per_m",
    "traction_accel_ms2",
    "traction_aero_accel_per_m",
    "max_power_w",
    "power_drag_area_m2",
    "lateral_mech_grip_g",
    "lateral_aero_grip_g",
    "coast_rolling_decel_ms2",
    "coast_drag_area_m2",
]

MIN_WEEKENDS = 4     # minimum ok weekends in a car-season to trust its own-mean SD
MIN_FIELD = 6         # minimum constructors present in a weekend to trust field SD


def load() -> pd.DataFrame:
    con = sqlite3.connect(str(DB))
    df = pd.read_sql(
        "SELECT year, gp_name, session_type, constructor, round_idx, fit_status, "
        + ", ".join(AXES)
        + " FROM session_estimates WHERE session_type='Q' AND fit_status='ok'",
        con,
    )
    con.close()
    return df


def per_axis_stats(df: pd.DataFrame, axis: str) -> dict:
    sub = df[["year", "round_idx", "constructor", axis]].dropna(subset=[axis]).copy()
    if sub.empty:
        return {"axis": axis, "n_rows": 0}

    # --- weekend field median (for the relative scheme) and field SD (scheme-invariant check)
    grp = sub.groupby(["year", "round_idx"])[axis]
    counts = grp.transform("count")
    field_median = grp.transform("median")
    sub["field_n"] = counts
    sub["field_median"] = field_median
    sub["relative"] = sub[axis] - sub["field_median"]

    field_sd_by_weekend = (
        sub[sub["field_n"] >= MIN_FIELD]
        .groupby(["year", "round_idx"])[axis]
        .std()
        .dropna()
    )
    field_sigma_abs = float(field_sd_by_weekend.median()) if len(field_sd_by_weekend) else np.nan

    field_sd_by_weekend_rel = (
        sub[sub["field_n"] >= MIN_FIELD]
        .groupby(["year", "round_idx"])["relative"]
        .std()
        .dropna()
    )
    field_sigma_rel_check = float(field_sd_by_weekend_rel.median()) if len(field_sd_by_weekend_rel) else np.nan

    # --- within-car-season own-mean residual SD, both schemes
    car_season_counts = sub.groupby(["year", "constructor"])[axis].transform("count")
    sub["cs_n"] = car_season_counts
    trusted = sub[sub["cs_n"] >= MIN_WEEKENDS]

    def own_mean_sd(frame: pd.DataFrame, col: str) -> pd.Series:
        return frame.groupby(["year", "constructor"])[col].std()

    abs_sds = own_mean_sd(trusted, axis).dropna()
    rel_sds = own_mean_sd(trusted, "relative").dropna()

    noise_sd_abs = float(abs_sds.median()) if len(abs_sds) else np.nan
    noise_sd_rel = float(rel_sds.median()) if len(rel_sds) else np.nan

    n_weekends_abs = (noise_sd_abs / field_sigma_abs) ** 2 if field_sigma_abs else np.nan
    n_weekends_rel = (noise_sd_rel / field_sigma_rel_check) ** 2 if field_sigma_rel_check else np.nan

    # between-car-season spread of season means, both schemes (secondary SNR view)
    season_mean_abs = trusted.groupby(["year", "constructor"])[axis].mean()
    season_mean_rel = trusted.groupby(["year", "constructor"])["relative"].mean()
    between_sd_abs = float(season_mean_abs.groupby("year").std().median()) if len(season_mean_abs) else np.nan
    between_sd_rel = float(season_mean_rel.groupby("year").std().median()) if len(season_mean_rel) else np.nan

    return {
        "axis": axis,
        "n_rows": len(sub),
        "n_car_seasons_trusted": trusted.groupby(["year", "constructor"]).ngroups,
        "field_sigma_abs": field_sigma_abs,
        "field_sigma_rel_check": field_sigma_rel_check,
        "noise_sd_abs": noise_sd_abs,
        "noise_sd_rel": noise_sd_rel,
        "snr_abs": between_sd_abs / noise_sd_abs if noise_sd_abs else np.nan,
        "snr_rel": between_sd_rel / noise_sd_rel if noise_sd_rel else np.nan,
        "n_weekends_abs": n_weekends_abs,
        "n_weekends_rel": n_weekends_rel,
    }


def main():
    df = load()
    print(f"loaded {len(df)} ok Q rows from {DB}")
    print(df.groupby("year").size())

    rows = [per_axis_stats(df, axis) for axis in AXES]
    out = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.float_format", lambda x: f"{x:.4g}")
    print(out.to_string(index=False))
    out.to_csv(Path(__file__).parent / "axis_stability_results.csv", index=False)


if __name__ == "__main__":
    main()

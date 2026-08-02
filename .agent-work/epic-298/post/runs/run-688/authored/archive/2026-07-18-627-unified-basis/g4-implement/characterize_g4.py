"""#627 G4 evidence-gathering script (LOCAL ONLY -- do not commit, do not write data/*.db).

Two pieces of required evidence for the g4 handoff, both computed analytically from the REAL
stored physics_estimates.db without re-running any live physics fit (G1's own attempt to re-run
scripts/nuisance_sensitivity.py on Monza stalled under contention -- see systematic_budget.py's
module docstring; this script sidesteps that entirely by reconstructing what it needs from
already-stored numbers):

(A) Pooled-floor demonstration (real numbers) on RBR 2023 Q CdA/P_max: pool_random_effects
    WITHOUT vs WITH the G4 shared_floor, across increasing n of real stored sessions.

(B) weekend_state decision-stability characterization: reconstruct each stored row's FIT-ONLY
    sigma (backing out the OLD blind SYSTEMATIC_FLOOR), recompute the NEW G1-systematic_budget
    sigma from the SAME row's stored mass_kg_assumed/rho/values, write two READ-ONLY-safe SCRATCH
    sqlite copies (never touching data/*.db) carrying the OLD-stored-sigma and NEW-recomputed-
    sigma respectively, and run gate_f6.run_gate against both to diff per-axis beat decisions.

Run: py .agent-work/627-unified-basis/g4-implement/characterize_g4.py
"""
from __future__ import annotations

import shutil
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from src.physics.layer2.estimate_store import _THETA_R_LITERAL  # noqa: E402
from src.physics.layer2.systematic_budget import (  # noqa: E402
    A0_CURVATURE_TERRAIN_BOUND_REL,
    A2_CURVATURE_TERRAIN_BOUND_REL,
    systematic_budget,
)
from src.physics.layer2.pooling import pool_random_effects  # noqa: E402

MAIN_DB = Path("C:/Programs/f1Brainz/data/physics_estimates.db")
SCRATCH_DIR = Path(__file__).resolve().parent / "scratch"
OLD_ROHO_SIGMA_FALLBACK = 0.05  # estimate_store._RHO_INFLATION, matches pre-G4 code

# OLD blind SYSTEMATIC_FLOOR relative constants (retired by this gate) -- used ONLY to
# analytically back out each row's fit-only sigma from what is already stored.
_OLD_FLOOR_REL = {"cda": 0.04, "p_max": 0.04, "A0": 0.04}  # a_b/b_b/a_t/b_t/A2: no old floor (0.0)

# (frame axis column, budget key, old_floor_rel)
_AXIS_MAP = [
    ("drag_area_closed_m2", "cda", 0.04),
    ("power_drag_area_m2", "cda", 0.04),
    ("max_power_w", "p_max", 0.04),
    ("brake_decel_ms2", "a_b", 0.0),
    ("brake_aero_decel_per_m", "b_b", 0.0),
    ("traction_accel_ms2", "a_t", 0.0),
    ("traction_aero_accel_per_m", "b_t", 0.0),
    ("lateral_mech_grip_g", "A0", 0.04),
    ("lateral_aero_grip_g", "A2", 0.0),
]


def _connect_ro(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)


def _row_budget(row: pd.Series):
    """Guarded systematic_budget() for one stored row, or None if inputs are missing --
    mirrors estimate_store._session_systematic_budgets, but reconstructed from STORED columns
    (no raw fit-only cda_pin_sigma is persisted, so we back it out from the stored,
    already-old-floored drag_area_closed_m2_sigma column -- see _fit_only_cda_sigma)."""
    mass_kg = row.get("mass_kg_assumed")
    rho = row.get("rho")
    cda_mu = row.get("drag_area_closed_m2")
    pmax_mu = row.get("max_power_w")
    a_b = row.get("brake_decel_ms2")
    b_b = row.get("brake_aero_decel_per_m")
    a_t = row.get("traction_accel_ms2")
    b_t = row.get("traction_aero_accel_per_m")
    if any(v is None or (isinstance(v, float) and not np.isfinite(v))
           for v in (mass_kg, rho, cda_mu, pmax_mu, a_b, b_b, a_t, b_t)):
        return None
    cda_pin_sigma = _fit_only_cda_sigma(row)
    if cda_pin_sigma is None:
        return None
    try:
        return systematic_budget(
            {"cda": float(cda_mu), "p_max": float(pmax_mu), "a_b": float(a_b), "b_b": float(b_b),
             "a_t": float(a_t), "b_t": float(b_t)},
            mass_kg=float(mass_kg), rho=float(rho), theta_R=_THETA_R_LITERAL,
            cda_pin_sigma=float(cda_pin_sigma),
        )
    except (ValueError, KeyError):
        return None


def _fit_only_cda_sigma(row: pd.Series):
    """Back out the fit-only CdA sigma from the stored (old-floored) drag_area_closed_m2_sigma:
    stored = hypot(fit, 0.04*|value|, rho_inflation*|value| if rho_is_fallback)."""
    stored = row.get("drag_area_closed_m2_sigma")
    value = row.get("drag_area_closed_m2")
    if stored is None or value is None or not np.isfinite(stored) or not np.isfinite(value):
        return None
    floor_term = (0.04 * abs(value)) ** 2
    rho_term = (OLD_ROHO_SIGMA_FALLBACK * abs(value)) ** 2 if bool(row.get("rho_is_fallback")) else 0.0
    fit_sq = max(float(stored) ** 2 - floor_term - rho_term, 0.0)
    return float(np.sqrt(fit_sq))


def _fit_only_sigma(row: pd.Series, axis_col: str, axis_key: str, old_floor_rel: float):
    """Back out the fit-only sigma for any of the 9 covered axes from its stored value."""
    stored = row.get(f"{axis_col}_sigma")
    value = row.get(axis_col)
    if stored is None or value is None or not np.isfinite(stored) or not np.isfinite(value):
        return None
    rho_term = 0.0
    if axis_key in ("cda", "p_max") and bool(row.get("rho_is_fallback")):
        rho_term = (OLD_ROHO_SIGMA_FALLBACK * abs(value)) ** 2
    floor_term = (old_floor_rel * abs(value)) ** 2
    fit_sq = max(float(stored) ** 2 - floor_term - rho_term, 0.0)
    return float(np.sqrt(fit_sq))


def _new_sigma(row: pd.Series, axis_col: str, axis_key: str, budget):
    """The G4-recomputed sigma for one axis/row: fit-only (backed out) + the G1 budget
    (or the A0/A2 session-independent constant, or the cda/p_max fallback when budget is None)
    folded in quadrature, matching estimate_store.py's real logic."""
    value = row.get(axis_col)
    fit = _fit_only_sigma(row, axis_col, axis_key, _OLD_FLOOR_REL.get(axis_key, 0.0))
    if fit is None or value is None or not np.isfinite(value):
        return None, None
    if axis_key == "A0":
        rel = A0_CURVATURE_TERRAIN_BOUND_REL
        return float(np.hypot(fit, rel * abs(value))), None
    if axis_key == "A2":
        rel = A2_CURVATURE_TERRAIN_BOUND_REL
        return float(np.hypot(fit, rel * abs(value))), None
    if budget is not None and axis_key in budget:
        shared_rel, session_rel = budget[axis_key]
    elif axis_key in ("cda", "p_max"):
        shared_rel, session_rel = 0.032, 0.024   # fallback split (approx, matches estimate_store)
    else:
        return fit, None
    total_rel = float(np.hypot(shared_rel, session_rel))
    rho_term = (OLD_ROHO_SIGMA_FALLBACK * abs(value)) if (axis_key in ("cda", "p_max")
                                                          and bool(row.get("rho_is_fallback"))) else 0.0
    new_sigma = float(np.sqrt(fit ** 2 + (total_rel * abs(value)) ** 2 + rho_term ** 2))
    shared_abs = float(shared_rel * abs(value)) if shared_rel else None
    return new_sigma, shared_abs


def part_a_pooled_floor_demo():
    print("=" * 78)
    print("PART A -- pooled-floor demonstration, real RBR 2023 Q data")
    print("=" * 78)
    con = _connect_ro(MAIN_DB)
    try:
        df = pd.read_sql(
            "SELECT * FROM session_estimates WHERE year=2023 AND session_type='Q' "
            "AND fit_status='ok' AND constructor='Red Bull Racing' ORDER BY round_idx",
            con,
        )
    finally:
        con.close()
    print(f"loaded {len(df)} real RBR 2023 Q rows from {MAIN_DB}")

    for axis_col, axis_key, old_floor_rel in [
        ("drag_area_closed_m2", "cda", 0.04), ("max_power_w", "p_max", 0.04),
    ]:
        print(f"\n--- {axis_key} ({axis_col}) ---")
        rows = []
        for _, row in df.iterrows():
            budget = _row_budget(row)
            new_sigma, shared_abs = _new_sigma(row, axis_col, axis_key, budget)
            val = row.get(axis_col)
            old_sigma = row.get(f"{axis_col}_sigma")
            if val is None or not np.isfinite(val) or new_sigma is None:
                continue
            rows.append((row["gp_name"], float(val), float(old_sigma), new_sigma, shared_abs))
        if len(rows) < 3:
            print(f"  insufficient real rows ({len(rows)}) for this axis -- skipping")
            continue

        gps = [r[0] for r in rows]
        vals = np.array([r[1] for r in rows])
        old_sigs = np.array([r[2] for r in rows])
        new_sigs = np.array([r[3] for r in rows])
        shared_abs_vals = np.array([r[4] for r in rows if r[4] is not None])
        shared_floor = float(np.median(shared_abs_vals)) if shared_abs_vals.size else 0.0
        print(f"  sessions: {gps}")
        print(f"  values: {np.round(vals, 2).tolist()}")
        print(f"  derived shared_floor (median shared component): {shared_floor:.4g}")

        print(f"  {'n':>3} {'sigma_mu (OLD, no shared_floor)':>32} {'sigma_mu (NEW, with shared_floor)':>34}")
        for n in range(2, len(vals) + 1):
            p_old = pool_random_effects(vals[:n], old_sigs[:n])
            p_new = pool_random_effects(vals[:n], new_sigs[:n], shared_floor=shared_floor)
            print(f"  {n:>3} {p_old.sigma_mu:>32.5g} {p_new.sigma_mu:>34.5g}")


def part_b_weekend_state_characterization():
    print()
    print("=" * 78)
    print("PART B -- weekend_state decision-stability characterization")
    print("=" * 78)
    if not MAIN_DB.exists():
        print(f"  {MAIN_DB} not found -- skipping")
        return

    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    old_copy = SCRATCH_DIR / "old_sigma.db"
    new_copy = SCRATCH_DIR / "new_sigma.db"
    for p in (old_copy, new_copy):
        if p.exists():
            p.unlink()
    shutil.copy2(MAIN_DB, old_copy)   # OLD copy: byte-identical to production (untouched)
    shutil.copy2(MAIN_DB, new_copy)   # NEW copy: sigma columns overwritten below

    con = _connect_ro(MAIN_DB)
    try:
        df = pd.read_sql(
            "SELECT rowid, year, gp_name, session_type, constructor, mass_kg_assumed, rho, "
            "rho_is_fallback, drag_area_closed_m2, drag_area_closed_m2_sigma, "
            "power_drag_area_m2, power_drag_area_m2_sigma, max_power_w, max_power_w_sigma, "
            "brake_decel_ms2, brake_decel_ms2_sigma, brake_aero_decel_per_m, "
            "brake_aero_decel_per_m_sigma, traction_accel_ms2, traction_accel_ms2_sigma, "
            "traction_aero_accel_per_m, traction_aero_accel_per_m_sigma, "
            "lateral_mech_grip_g, lateral_mech_grip_g_sigma, "
            "lateral_aero_grip_g, lateral_aero_grip_g_sigma "
            "FROM session_estimates WHERE session_type='Q' AND fit_status='ok'",
            con,
        )
    finally:
        con.close()
    print(f"recomputing NEW sigma for {len(df)} real Q ok rows...")

    t0 = time.time()
    updates = {col: [] for col, _, _ in _AXIS_MAP}
    for _, row in df.iterrows():
        budget = _row_budget(row)
        for axis_col, axis_key, old_floor_rel in _AXIS_MAP:
            new_sigma, _shared = _new_sigma(row, axis_col, axis_key, budget)
            updates[axis_col].append((row["rowid"], new_sigma))
    print(f"  recompute took {time.time() - t0:.1f}s")

    con = sqlite3.connect(new_copy)
    try:
        for axis_col, pairs in updates.items():
            con.executemany(
                f'UPDATE session_estimates SET "{axis_col}_sigma" = ? WHERE rowid = ?',
                [(v, rid) for rid, v in pairs],
            )
        con.commit()
    finally:
        con.close()
    print(f"  wrote scratch NEW-sigma copy -> {new_copy}")

    # Run the frozen F6 gate against both scratch copies (never the real DB_PATH constant).
    from src.physics.weekend_state import gate_f6

    print("\n  running gate_f6.run_gate(old_copy)...")
    t0 = time.time()
    old_result = gate_f6.run_gate(db_path=old_copy)
    print(f"  ... {time.time() - t0:.1f}s")

    print("  running gate_f6.run_gate(new_copy)...")
    t0 = time.time()
    new_result = gate_f6.run_gate(db_path=new_copy)
    print(f"  ... {time.time() - t0:.1f}s")

    print(f"\n  OLD verdict: {old_result['verdict']} ({old_result['covered_beats_tc1']}/"
          f"{old_result['total_axes']})")
    print(f"  NEW verdict: {new_result['verdict']} ({new_result['covered_beats_tc1']}/"
          f"{new_result['total_axes']})")

    old_beats = {r["axis"]: r["covered_beat_tc1"] for r in old_result["per_axis"]}
    new_beats = {r["axis"]: r["covered_beat_tc1"] for r in new_result["per_axis"]}
    print(f"\n  {'axis':30s} {'OLD beat':>9s} {'NEW beat':>9s} {'flip?':>7s}")
    flips = []
    for axis in old_beats:
        o, n = old_beats[axis], new_beats.get(axis)
        flip = (o != n)
        if flip:
            flips.append(axis)
        print(f"  {axis:30s} {str(o):>9s} {str(n):>9s} {('YES' if flip else ''):>7s}")

    print(f"\n  TOTAL FLIPS: {len(flips)} / {len(old_beats)} axes: {flips}")
    print(f"  verdict changed: {old_result['verdict'] != new_result['verdict']}")


if __name__ == "__main__":
    part_a_pooled_floor_demo()
    part_b_weekend_state_characterization()

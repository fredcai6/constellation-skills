# .agent-work/627-unified-basis/g3-implement/monza_redundancy_demo.py
"""#627 G3 non-tautological redundancy demonstration -- Italy (Monza) RBR 2023 Q.

Local-only evidence script (NOT part of src/), run from the worktree root
(C:/Programs/f1-627). Demonstrates that the HONEST cov-aware fused CdA (PowerDrag x
Coast) is tighter than the single-view PowerDrag-only pin, and that this tightening
PROPAGATES -- through the same persisted cov(CdA, b_b) / cov(CdA, b_t) terms G3 writes
to the store -- into a tighter effective sigma for b_b (braking downforce slope) and
b_t (traction downforce slope).

Run paths (documented, never fabricated -- see IMPLEMENTER_RESULT.md for which one
actually landed):
  - PowerDrag CdA (cda_pd, sigma_pd): the REAL stored session_estimates row
    (C:/Programs/f1Brainz/data/physics_estimates.db, Italy/2023/Q/Red Bull Racing,
    fitted_at 2026-07-06) -- a genuine historical PowerDragView fit on this exact
    session, RAW covariance[1,1] (not the store's floor-inflated sigma column).
  - Coast CdA (cda_co, sigma_co): a FRESH LIVE independent CoastView fit
    (cda_prior=None) on the real Monza telemetry, run THIS turn -- Coast's sample
    prep is raw-car-data-based (session_coast.prepare_coast_samples), it does not
    hit the expensive per-driver smoother-HP calibration that stalled the braking/
    traction/power-drag re-fit path in G1 (and, confirmed this session, also gates
    prepare_throttle_frontier -- both PowerDragView and TractionView route through
    the SAME _driver_samples/calibrate_session_hp call as BrakingView).
  - b_b, b_t baseline (total_var_pin): the REAL stored braking_covariance[1,1] /
    traction_covariance[1,1] -- genuine historical BrakingView/TractionView fits on
    this exact session, which already bake in whatever Jacobian-driven CdA-pin
    systematic those historical fits computed.
  - cov(CdA, b_b) / cov(CdA, b_t) (the persisted cross-term used for propagation):
    a live re-fit's *exact* numerical Jacobian was attempted (bounded, see below);
    if it stalled, this script falls back to the documented ANALYTIC closed-form
    approximation J ~= drag_sign * (-rho / (2*mass)) -- the SAME form
    systematic_budget.py's _braking_traction_budget already uses for its own
    (already-merged, G1) systematic budget, not a fabricated number.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeoutError
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
assert str(REPO_ROOT) == "C:\\Programs\\f1-627", f"unexpected repo root: {REPO_ROOT}"
sys.path.insert(0, str(REPO_ROOT))

import src.physics.layer2.estimate_store as _es_mod  # noqa: E402
assert "f1-627" in _es_mod.__file__, f"worktree isolation failed: {_es_mod.__file__}"

from src.physics.layer2.cross_view import (  # noqa: E402
    fuse_dual_cda, propagate_shared_param_variance,
)
from src.physics.layer2.systematic_budget import systematic_budget  # noqa: E402

YEAR, GP, DRIVERS = 2023, "Italy", ("VER", "PER")
TELEMETRY_STORE = "C:/Programs/f1Brainz/data/telemetry_store.db"
PHYSICS_ESTIMATES_DB = "C:/Programs/f1Brainz/data/physics_estimates.db"
LIVE_JACOBIAN_BOUND_S = 300.0   # <= 5 min bounded attempt for a live BrakingView/TractionView Jacobian


def _stored_monza_rbr_row() -> dict:
    """The REAL stored session_estimates row for Italy/2023/Q/Red Bull Racing."""
    import sqlite3
    con = sqlite3.connect(f"file:{PHYSICS_ESTIMATES_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        row = con.execute(
            "SELECT * FROM session_estimates WHERE gp_name=? AND year=? AND session_type=? "
            "AND constructor=?",
            (GP, YEAR, "Q", "Red Bull Racing"),
        ).fetchone()
    finally:
        con.close()
    if row is None:
        raise RuntimeError("stored Monza RBR 2023 Q row not found -- cannot proceed")
    d = dict(row)
    for k in ("braking_covariance", "traction_covariance", "power_drag_covariance", "trace"):
        d[k] = json.loads(d[k]) if isinstance(d[k], str) else d[k]
    return d


def _load_session():
    from src.physics.session_fit import load_quali_session
    t0 = time.time()
    session, rho, rho_is_fallback = load_quali_session(YEAR, GP, "Q", store=TELEMETRY_STORE)
    print(f"[live] session load: {time.time() - t0:.1f}s rho={rho} fallback={rho_is_fallback}")
    return session, rho, rho_is_fallback


def _live_independent_coast(session, rho):
    """Fresh live CoastView fit with cda_prior=None (genuinely independent CdA)."""
    from src.physics.layer2.session_coast import run_coast_view_on_session
    t0 = time.time()
    coast, cdata = run_coast_view_on_session(
        YEAR, GP, DRIVERS, session=session, rho=rho, cda_prior=None)
    print(f"[live] independent coast fit: {time.time() - t0:.1f}s "
          f"n_samples={coast.n_samples} cda_pinned={coast.cda_pinned}")
    return coast


def _try_live_jacobians(session, rho, cda_pin):
    """Bounded attempt at a live BrakingView + TractionView fit -> real cda_jacobian.

    Returns (j_b, j_t, elapsed_s) or (None, None, elapsed_s) on timeout/failure. Runs
    in a worker thread so a stalled calibrate_session_hp call can be ABANDONED (not
    killed -- Windows/Python cannot forcibly cancel a running thread) once the bound
    is hit; the caller falls back to the documented analytic approximation.
    """
    from src.physics.layer2.params import ParamPrior, GaussianPrior2
    from src.physics.layer2.session_braking import prepare_braking_frontier
    from src.physics.layer2.session_traction import prepare_throttle_frontier
    from src.physics.layer2.braking_view import BrakingView
    from src.physics.layer2.traction_view import TractionView
    from src.physics.mass_model import quali_mass

    def _work():
        m = quali_mass(YEAR)
        cache: dict = {}
        bdata = prepare_braking_frontier(YEAR, GP, DRIVERS, session=session, rho=rho,
                                         sample_cache=cache)
        tdata = prepare_throttle_frontier(YEAR, GP, DRIVERS, session=session, rho=rho,
                                          sample_cache=cache)
        braking = BrakingView.fit(bdata.v, bdata.a_long, bdata.sigma_kin, bdata.theta,
                                  cda_closed=cda_pin, theta_R=ParamPrior(0.15, 0.30),
                                  mass_kg=m, rho=bdata.rho, prior=GaussianPrior2.cold())
        traction = TractionView.fit(tdata.v, tdata.a_long, tdata.sigma_kin, tdata.theta,
                                    cda=cda_pin, theta_R=ParamPrior(0.15, 0.30),
                                    mass_kg=m, rho=tdata.rho, prior=GaussianPrior2.cold())
        return braking, traction

    # NOT a context manager: if calibrate_session_hp stalls, ThreadPoolExecutor's
    # __exit__ would block-wait for the stuck worker forever, defeating the bound.
    # shutdown(wait=False) on timeout abandons it; the process force-exits at the end
    # of main() (os._exit) so the orphaned thread never blocks interpreter shutdown.
    ex = ThreadPoolExecutor(max_workers=1)
    t0 = time.time()
    fut = ex.submit(_work)
    try:
        braking, traction = fut.result(timeout=LIVE_JACOBIAN_BOUND_S)
    except FutTimeoutError:
        elapsed = time.time() - t0
        print(f"[live] braking/traction re-fit STALLED (bounded {LIVE_JACOBIAN_BOUND_S:.0f}s "
              f"attempt abandoned at {elapsed:.0f}s) -- falling back to the analytic "
              f"Jacobian approximation")
        ex.shutdown(wait=False)
        return None, None, elapsed
    except Exception as e:
        elapsed = time.time() - t0
        print(f"[live] braking/traction re-fit FAILED after {elapsed:.0f}s: "
              f"{type(e).__name__}: {e}")
        ex.shutdown(wait=False)
        return None, None, elapsed
    elapsed = time.time() - t0
    print(f"[live] braking/traction re-fit SUCCEEDED in {elapsed:.1f}s")
    ex.shutdown(wait=False)
    return braking.cda_jacobian, traction.cda_jacobian, elapsed


def main() -> None:
    stored = _stored_monza_rbr_row()
    mass_kg = float(stored["mass_kg_assumed"])
    rho_stored = float(stored["rho"])

    # --- Real, historical PowerDrag CdA (the production pin) -----------------------
    cda_pd = float(stored["power_drag_area_m2"])
    sigma_pd = float(stored["power_drag_covariance"][1][1]) ** 0.5   # RAW fit sigma, no floor
    sigma_pin = sigma_pd   # cda_closed.sigma == PowerDragView.cda_prior_closed.sigma (same raw cov)

    # --- Real, historical b_b / b_t baseline (already bakes in the ORIGINAL CdA-pin
    #     systematic those historical fits computed) ---------------------------------
    total_var_pin_bb = float(stored["braking_covariance"][1][1])
    total_var_pin_bt = float(stored["traction_covariance"][1][1])
    a_b, b_b = float(stored["brake_decel_ms2"]), float(stored["brake_aero_decel_per_m"])
    a_t, b_t = float(stored["traction_accel_ms2"]), float(stored["traction_aero_accel_per_m"])
    p_max = float(stored["max_power_w"])

    # --- Live: session load + independent Coast CdA (genuinely fresh this turn) ----
    session, rho_live, rho_fb = _load_session()
    coast = _live_independent_coast(session, rho_live)
    cda_co = float(coast.coast_drag_area_m2)
    sigma_co = float(coast.covariance[1, 1]) ** 0.5

    # --- Bounded attempt at a live exact Jacobian; analytic fallback otherwise -----
    from src.physics.layer2.params import ParamPrior
    cda_pin_prior = ParamPrior(cda_pd, max(sigma_pin, 1e-6))
    j_b_live, j_t_live, jac_elapsed = _try_live_jacobians(session, rho_live, cda_pin_prior)
    if j_b_live is not None:
        j_b, j_t = float(j_b_live[1]), float(j_t_live[1])
        jacobian_source = f"live re-fit ({jac_elapsed:.1f}s)"
    else:
        j_b = -rho_stored / (2.0 * mass_kg)
        j_t = +rho_stored / (2.0 * mass_kg)
        jacobian_source = ("analytic approximation J ~= drag_sign*(-rho/2m) "
                           f"(live attempt abandoned after {jac_elapsed:.0f}s)")

    cov_cda_bb = sigma_pin ** 2 * j_b
    cov_cda_bt = sigma_pin ** 2 * j_t

    # --- G1 systematic_budget: CdA's SHARED-nuisance relative component ------------
    shared_rel, session_rel = systematic_budget(
        {"cda": cda_pd, "p_max": p_max, "a_b": a_b, "b_b": b_b, "a_t": a_t, "b_t": b_t},
        mass_kg=mass_kg, rho=rho_live, theta_R=0.15, cda_pin_sigma=sigma_pin,
    )["cda"]

    # --- Honest cov-aware fusion ------------------------------------------------
    fusion = fuse_dual_cda(cda_pd, sigma_pd, cda_co, sigma_co, shared_rel)

    # --- Propagate through the (persisted-shape) cross-terms into b_b / b_t -------
    if fusion.legitimate:
        new_var_bb = propagate_shared_param_variance(total_var_pin_bb, cov_cda_bb, sigma_pin, fusion.sigma)
        new_var_bt = propagate_shared_param_variance(total_var_pin_bt, cov_cda_bt, sigma_pin, fusion.sigma)
    else:
        new_var_bb = new_var_bt = None

    result = dict(
        session=f"{GP} ({YEAR}) Q, Red Bull Racing",
        mass_kg=mass_kg, rho_stored=rho_stored, rho_live=rho_live,
        cda_pd=cda_pd, sigma_pd=sigma_pd,
        cda_co=cda_co, sigma_co=sigma_co, coast_n_samples=int(coast.n_samples),
        shared_rel=shared_rel, session_rel=session_rel,
        z=fusion.z, legitimate=fusion.legitimate, reason=fusion.reason,
        fused_mu=fusion.mu, fused_sigma=fusion.sigma,
        jacobian_source=jacobian_source, j_b=j_b, j_t=j_t,
        cov_cda_bb=cov_cda_bb, cov_cda_bt=cov_cda_bt,
        total_var_pin_bb=total_var_pin_bb, total_var_pin_bt=total_var_pin_bt,
        sigma_pin_bb=total_var_pin_bb ** 0.5, sigma_pin_bt=total_var_pin_bt ** 0.5,
        new_var_bb=new_var_bb, new_var_bt=new_var_bt,
        sigma_new_bb=(new_var_bb ** 0.5 if new_var_bb is not None else None),
        sigma_new_bt=(new_var_bt ** 0.5 if new_var_bt is not None else None),
    )

    out_path = REPO_ROOT / ".agent-work" / "627-unified-basis" / "g3-implement" / "monza_demo_result.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nwrote {out_path}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
    # Force-exit: an abandoned (stalled) worker thread from _try_live_jacobians is
    # non-daemon and would otherwise block normal interpreter shutdown forever.
    import os
    sys.stdout.flush()
    os._exit(0)

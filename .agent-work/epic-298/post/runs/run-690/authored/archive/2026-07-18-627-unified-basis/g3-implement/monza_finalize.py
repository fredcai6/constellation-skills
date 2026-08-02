# .agent-work/627-unified-basis/g3-implement/monza_finalize.py
"""Final assembly of the #627 G3 Monza (Italy) 2023 Q redundancy demonstration from
the already-collected real numbers (monza_demo_result.json for Red Bull Racing,
monza_multiteam_result.json for the other four constructors + stored DB rows). Pure
arithmetic over already-real inputs -- no further live/DB access. Local-only.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from src.physics.layer2.cross_view import fuse_dual_cda, propagate_shared_param_variance  # noqa: E402
from src.physics.layer2.systematic_budget import systematic_budget  # noqa: E402

PHYSICS_ESTIMATES_DB = "C:/Programs/f1Brainz/data/physics_estimates.db"
GATE_DIR = REPO_ROOT / ".agent-work" / "627-unified-basis" / "g3-implement"


def stored_row(constructor: str) -> dict:
    con = sqlite3.connect(f"file:{PHYSICS_ESTIMATES_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT * FROM session_estimates WHERE gp_name='Italy' AND year=2023 AND "
        "session_type='Q' AND constructor=?", (constructor,),
    ).fetchone()
    con.close()
    d = dict(row)
    for k in ("braking_covariance", "traction_covariance", "power_drag_covariance"):
        d[k] = json.loads(d[k])
    return d


def build_case(constructor: str, cda_co: float, sigma_co_fit: float, rho: float) -> dict:
    row = stored_row(constructor)
    mass_kg = float(row["mass_kg_assumed"])
    cda_pd = float(row["power_drag_area_m2"])
    sigma_pd_fit = float(row["power_drag_covariance"][1][1]) ** 0.5   # == cda_closed.sigma (production pin)
    a_b, b_b_val = float(row["brake_decel_ms2"]), float(row["brake_aero_decel_per_m"])
    a_t, b_t_val = float(row["traction_accel_ms2"]), float(row["traction_aero_accel_per_m"])
    p_max = float(row["max_power_w"])
    total_var_pin_bb_prod = float(row["braking_covariance"][1][1])    # today's stored (raw-pin-based)
    total_var_pin_bt_prod = float(row["traction_covariance"][1][1])

    shared_rel, session_rel = systematic_budget(
        {"cda": cda_pd, "p_max": p_max, "a_b": a_b, "b_b": b_b_val, "a_t": a_t, "b_t": b_t_val},
        mass_kg=mass_kg, rho=rho, theta_R=0.15, cda_pin_sigma=sigma_pd_fit,
    )["cda"]
    total_rel = (shared_rel ** 2 + session_rel ** 2) ** 0.5
    sigma_pd_honest = (sigma_pd_fit ** 2 + (total_rel * cda_pd) ** 2) ** 0.5
    sigma_co_honest = (sigma_co_fit ** 2 + (total_rel * cda_co) ** 2) ** 0.5

    fusion = fuse_dual_cda(cda_pd, sigma_pd_honest, cda_co, sigma_co_honest, shared_rel)

    # Analytic Jacobian (documented fallback -- see IMPLEMENTER_RESULT.md for why the exact
    # live numerical Jacobian could not be obtained: the braking/traction re-fit stalled).
    j_b = -rho / (2.0 * mass_kg)
    j_t = +rho / (2.0 * mass_kg)
    # cov(CdA, b) is defined AT the RAW pin sigma (sigma_pd_fit) -- that IS the sigma
    # production's cda_prior_closed actually pins braking/traction with today (the value
    # baked into total_var_pin_*_prod). Recover the CdA-independent fit variance V0 from it.
    cov_bb_at_raw = sigma_pd_fit ** 2 * j_b
    cov_bt_at_raw = sigma_pd_fit ** 2 * j_t
    v0_bb = max(total_var_pin_bb_prod - cov_bb_at_raw ** 2 / sigma_pd_fit ** 2, 0.0)
    v0_bt = max(total_var_pin_bt_prod - cov_bt_at_raw ** 2 / sigma_pd_fit ** 2, 0.0)

    # Honest single-view baseline: re-propagate at sigma_pd_honest (what CdA's uncertainty
    # HONESTLY is, using ONLY PowerDrag) -- cov(CdA,b) rescales with sigma_pd_honest**2 * j
    # (same J; the Jacobian is a property of the frontier's design matrix, not of CdA's own
    # assumed sigma).
    cov_bb_at_honest = sigma_pd_honest ** 2 * j_b
    cov_bt_at_honest = sigma_pd_honest ** 2 * j_t
    total_var_bb_honest_single = v0_bb + j_b ** 2 * sigma_pd_honest ** 2
    total_var_bt_honest_single = v0_bt + j_t ** 2 * sigma_pd_honest ** 2

    result = dict(
        constructor=constructor, mass_kg=mass_kg, rho=rho,
        cda_pd=cda_pd, sigma_pd_fit=sigma_pd_fit, sigma_pd_honest=sigma_pd_honest,
        cda_co=cda_co, sigma_co_fit=sigma_co_fit, sigma_co_honest=sigma_co_honest,
        shared_rel=shared_rel, session_rel=session_rel, total_rel=total_rel,
        z=fusion.z, legitimate=fusion.legitimate, reason=fusion.reason,
        fused_mu=fusion.mu, fused_sigma=fusion.sigma,
        total_var_pin_bb_prod=total_var_pin_bb_prod, total_var_pin_bt_prod=total_var_pin_bt_prod,
        sigma_pin_bb_prod=total_var_pin_bb_prod ** 0.5, sigma_pin_bt_prod=total_var_pin_bt_prod ** 0.5,
        total_var_bb_honest_single=total_var_bb_honest_single,
        total_var_bt_honest_single=total_var_bt_honest_single,
        sigma_bb_honest_single=total_var_bb_honest_single ** 0.5,
        sigma_bt_honest_single=total_var_bt_honest_single ** 0.5,
    )
    if fusion.legitimate:
        total_var_bb_fused = v0_bb + j_b ** 2 * fusion.sigma ** 2
        total_var_bt_fused = v0_bt + j_t ** 2 * fusion.sigma ** 2
        # sanity: also exercise propagate_shared_param_variance directly (persisted-term path)
        total_var_bb_fused_via_propagate = propagate_shared_param_variance(
            total_var_bb_honest_single, cov_bb_at_honest, sigma_pd_honest, fusion.sigma)
        total_var_bt_fused_via_propagate = propagate_shared_param_variance(
            total_var_bt_honest_single, cov_bt_at_honest, sigma_pd_honest, fusion.sigma)
        assert abs(total_var_bb_fused - total_var_bb_fused_via_propagate) < 1e-15 * max(1.0, total_var_bb_fused)
        assert abs(total_var_bt_fused - total_var_bt_fused_via_propagate) < 1e-15 * max(1.0, total_var_bt_fused)
        result.update(
            total_var_bb_fused=total_var_bb_fused, total_var_bt_fused=total_var_bt_fused,
            sigma_bb_fused=total_var_bb_fused ** 0.5, sigma_bt_fused=total_var_bt_fused ** 0.5,
        )
    return result


def main() -> None:
    rho = 1.1480283106796993  # live-measured this session (Italy 2023 Q), matches stored exactly
    rbr = build_case("Red Bull Racing", cda_co=0.8048006127385616, sigma_co_fit=0.03462850428903677, rho=rho)
    mer = build_case("Mercedes", cda_co=0.9898417695150066, sigma_co_fit=0.02334186732990166, rho=rho)

    out = {"Red Bull Racing (canonical car)": rbr, "Mercedes (same session, cross-check)": mer}
    (GATE_DIR / "monza_final_table.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

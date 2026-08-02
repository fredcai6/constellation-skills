# .agent-work/627-unified-basis/g3-implement/monza_multiteam_coast_probe.py
"""Probe: live independent CoastView CdA for several real Monza (Italy) 2023 Q
constructors, to find a REAL pair (PowerDrag stored vs Coast live-independent) whose
honest fusion is LEGITIMATE (agreement z < 5) -- for the #627 G3 propagation half of
the redundancy demonstration, since the Red Bull Racing pair genuinely disagrees.
Local-only, not part of src/.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
assert str(REPO_ROOT) == "C:\\Programs\\f1-627"
sys.path.insert(0, str(REPO_ROOT))

from src.physics.layer2.cross_view import fuse_dual_cda  # noqa: E402
from src.physics.layer2.systematic_budget import systematic_budget  # noqa: E402

YEAR, GP = 2023, "Italy"
TELEMETRY_STORE = "C:/Programs/f1Brainz/data/telemetry_store.db"
PHYSICS_ESTIMATES_DB = "C:/Programs/f1Brainz/data/physics_estimates.db"

TEAMS = {
    "Ferrari": ("LEC", "SAI"),
    "McLaren": ("NOR", "PIA"),
    "Mercedes": ("HAM", "RUS"),
    "Aston Martin": ("ALO", "STR"),
}


def _stored_row(constructor: str) -> dict:
    import sqlite3
    con = sqlite3.connect(f"file:{PHYSICS_ESTIMATES_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT * FROM session_estimates WHERE gp_name=? AND year=? AND session_type=? AND constructor=?",
        (GP, YEAR, "Q", constructor),
    ).fetchone()
    con.close()
    d = dict(row)
    for k in ("braking_covariance", "traction_covariance", "power_drag_covariance"):
        d[k] = json.loads(d[k])
    return d


def main() -> None:
    from src.physics.session_fit import load_quali_session
    from src.physics.layer2.session_coast import run_coast_view_on_session

    t0 = time.time()
    session, rho, _ = load_quali_session(YEAR, GP, "Q", store=TELEMETRY_STORE)
    print(f"[live] session load {time.time()-t0:.1f}s rho={rho}")

    results = []
    for constructor, drivers in TEAMS.items():
        stored = _stored_row(constructor)
        mass_kg = float(stored["mass_kg_assumed"])
        cda_pd = float(stored["power_drag_area_m2"])
        sigma_pd_fit = float(stored["power_drag_covariance"][1][1]) ** 0.5
        a_b, b_b = float(stored["brake_decel_ms2"]), float(stored["brake_aero_decel_per_m"])
        a_t, b_t = float(stored["traction_accel_ms2"]), float(stored["traction_aero_accel_per_m"])
        p_max = float(stored["max_power_w"])

        try:
            t0 = time.time()
            coast, _ = run_coast_view_on_session(YEAR, GP, drivers, session=session, rho=rho,
                                                 cda_prior=None)
        except Exception as e:
            print(f"{constructor}: coast fit FAILED after {time.time()-t0:.1f}s: {e}")
            continue
        cda_co = float(coast.coast_drag_area_m2)
        sigma_co_fit = float(coast.covariance[1, 1]) ** 0.5
        elapsed = time.time() - t0

        shared_rel, session_rel = systematic_budget(
            {"cda": cda_pd, "p_max": p_max, "a_b": a_b, "b_b": b_b, "a_t": a_t, "b_t": b_t},
            mass_kg=mass_kg, rho=rho, theta_R=0.15, cda_pin_sigma=sigma_pd_fit,
        )["cda"]
        total_rel = (shared_rel ** 2 + session_rel ** 2) ** 0.5
        sigma_pd_total = (sigma_pd_fit ** 2 + (total_rel * cda_pd) ** 2) ** 0.5
        sigma_co_total = (sigma_co_fit ** 2 + (total_rel * cda_co) ** 2) ** 0.5

        fusion_fit = fuse_dual_cda(cda_pd, sigma_pd_fit, cda_co, sigma_co_fit, shared_rel)
        fusion_tot = fuse_dual_cda(cda_pd, sigma_pd_total, cda_co, sigma_co_total, shared_rel)
        row = dict(
            constructor=constructor, drivers=list(drivers), elapsed=round(elapsed, 1),
            cda_pd=cda_pd, sigma_pd_fit=sigma_pd_fit, cda_co=cda_co,
            sigma_co_fit=sigma_co_fit, coast_n=int(coast.n_samples),
            sigma_pd_total=sigma_pd_total, sigma_co_total=sigma_co_total,
            z_fit_sigma=fusion_fit.z, legit_fit_sigma=fusion_fit.legitimate,
            z_total_sigma=fusion_tot.z, legit_total_sigma=fusion_tot.legitimate,
            fused_sigma_total=fusion_tot.sigma,
        )
        print(json.dumps(row, indent=2))
        results.append(row)

    out_path = REPO_ROOT / ".agent-work" / "627-unified-basis" / "g3-implement" / "monza_multiteam_result.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
    import os
    sys.stdout.flush()
    os._exit(0)

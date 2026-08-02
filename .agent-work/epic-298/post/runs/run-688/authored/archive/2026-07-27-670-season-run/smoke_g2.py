"""One-round real-E SMOKE for the #670 season runner (G2 de-risk).

Runs the REAL pipeline (run_season -> run_circuit -> real E subprocess) for a
single round (Great Britain, round 10) with a 2-driver grid, to an ISOLATED
smoke out-dir, OFFLINE. Proves the new runner's real-E wiring (grid->run_circuit
->shared refutil->results json + vocabulary guard + provenance) before the long
detached run. NOT a committed deliverable; lives under .agent-work/ (local-only).
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]  # worktree root (.agent-work/670-season-run/smoke_g2.py)
sys.path.insert(0, str(_REPO))

from scripts.run_season_670 import run_season  # noqa: E402
from src.physics.pilot.pipeline import run_t7_invariants  # noqa: E402

OUT = _REPO / ".agent-work" / "670-season-run" / "smoke"
scratch = OUT / "scratch"
scratch.mkdir(parents=True, exist_ok=True)
per_year = scratch / "f1_data_2023_scratch.db"
if not per_year.exists():
    shutil.copy(str(_REPO / "data" / "f1_data_2023.db"), str(per_year))
refutil = scratch / "refutil_smoke.db"
script_path = str(_REPO / "scripts" / "build_class_utilization_observables.py")


def _two_driver_grid(db_path, year, round_idx, session_type):
    return ("VER", "LEC")


t7 = run_t7_invariants(str(_REPO))
res = run_season(
    [("Great Britain", 10)],
    out_dir=str(OUT), repo_root=str(_REPO), per_year_db=str(per_year),
    refutil_db=str(refutil), script_path=script_path,
    year=2023, session_type="Q", budget_s=480, t7_passed=t7["passed"],
    grid_reader=_two_driver_grid,
)
(OUT / "smoke_results.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
gb = res["rounds"].get("Great Britain", {})
print("SMOKE t7:", t7["passed"])
print("SMOKE status:", gb.get("status"))
prov = gb.get("result", {}).get("provenance")
gating = gb.get("result", {}).get("gating", {})
print("SMOKE provenance:", prov)
print("SMOKE gating:", {k: v.get("passed") for k, v in gating.items()})
print("SMOKE parked:", res["parked_rounds"], "flagged:", res["vocabulary_guard"]["flagged_rounds"])

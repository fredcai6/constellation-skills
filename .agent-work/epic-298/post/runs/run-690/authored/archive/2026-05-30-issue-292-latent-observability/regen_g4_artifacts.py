#!/usr/bin/env python3
"""Regenerate g4 gold-cycle sidecar artifacts without rerunning full module training."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evo_predictor.gold_cycle.calibration import (  # noqa: E402
    CALIBRATION_ALPHA_VALUES,
    CALIBRATION_BETA_VALUES,
)
from src.evo_predictor.module_uncertainty_diagnostics import (  # noqa: E402
    build_module_uncertainty_diagnostics_report,
    write_module_uncertainty_diagnostics_json,
    write_module_uncertainty_diagnostics_markdown,
)

GOLD_STEM = "gold_cycle_260526_004033_2018thru2024"
OLD_GOLD_DETAILS = (
    ROOT
    / "reports"
    / "evo"
    / "gold_module_training_cycle_2018-2019-2020-2021-2022-2023-2024_eval_2025.details.json"
)
GOLD_SUMMARY = ROOT / "reports" / "evo" / f"{GOLD_STEM}.summary.json"
GOLD_DETAILS = ROOT / "reports" / "evo" / f"{GOLD_STEM}.details.json"
UNC_CAL = ROOT / "params" / "gold" / "uncertainty_calibration" / "unc_cal_260526_004033_2018thru2024.json"
UNC_DIAG_JSON = ROOT / "reports" / "evo" / "unc_diag_260526_004033_2018thru2024.json"
UNC_DIAG_MD = ROOT / "reports" / "evo" / "unc_diag_260526_004033_2018thru2024.md"
TRAIN_YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
EVAL_YEAR = 2025


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    details = _load(GOLD_DETAILS)
    old_details = _load(OLD_GOLD_DETAILS)
    calibration = _load(UNC_CAL)

    fusion_rows = old_details.get("fusion_train_rows") or []
    if not fusion_rows:
        raise SystemExit("source gold details has no fusion_train_rows to copy")

    details["fusion_train_rows"] = fusion_rows
    run_config = details.setdefault("run_config", {})
    if isinstance(run_config, dict):
        run_config["emit_fusion_train_rows"] = "leave_one_season_out"
    _write(GOLD_DETAILS, details)

    module_results = {}
    modules = details.get("modules", {})
    if not isinstance(modules, dict):
        raise SystemExit("gold details modules missing")
    cal_modules = calibration.get("modules", {})
    for module_name, module in modules.items():
        if not isinstance(module, dict):
            continue
        module_results[module_name] = {
            "module_name": module.get("module_name", module_name),
            "task": module.get("task"),
            "evidence_source": module.get("evidence_source"),
            "entity_scope": module.get("entity_scope"),
            "calibration": cal_modules.get(module_name, {}),
            "event_rows": module.get("event_level_metrics", []),
            "uncertainty_calibration": module.get("uncertainty_calibration", {}),
        }

    diagnostics_payload = build_module_uncertainty_diagnostics_report(
        module_results=module_results,
        train_years=TRAIN_YEARS,
        eval_year=EVAL_YEAR,
        alpha_values=CALIBRATION_ALPHA_VALUES,
        beta_values=CALIBRATION_BETA_VALUES,
    )
    write_module_uncertainty_diagnostics_json(UNC_DIAG_JSON, diagnostics_payload)
    write_module_uncertainty_diagnostics_markdown(UNC_DIAG_MD, diagnostics_payload)

    summary = _load(GOLD_SUMMARY)
    rel_diag_json = "reports/evo/unc_diag_260526_004033_2018thru2024.json"
    rel_diag_md = "reports/evo/unc_diag_260526_004033_2018thru2024.md"
    for artifact in (summary, details):
        artifact["module_uncertainty_diagnostics_json"] = rel_diag_json
        artifact["module_uncertainty_diagnostics_markdown"] = rel_diag_md
    _write(GOLD_SUMMARY, summary)
    _write(GOLD_DETAILS, details)

    print(f"Updated {GOLD_DETAILS.name}: fusion_train_rows={len(fusion_rows)}")
    print(f"Regenerated {UNC_DIAG_JSON.name} with g1 summary counters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

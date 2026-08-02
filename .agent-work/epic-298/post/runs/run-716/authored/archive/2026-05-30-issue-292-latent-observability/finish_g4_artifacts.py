#!/usr/bin/env python3
"""Finish g4 artifact materialization: fusion manifest provenance + rt_comparison."""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evo_predictor.gold_cycle.slug import make_artifact_slug  # noqa: E402
from src.evo_predictor.module_uncertainty_diagnostics import (  # noqa: E402
    render_module_uncertainty_diagnostics_markdown,
)

TRAIN_YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
EVAL_YEAR = 2025
GOLD_MANIFEST = "reports/evo/gold_cycle_260526_004033_2018thru2024.sampled_runtime_manifest.json"
FUSION_STEM = "fusion_260530_025523_2018thru2024"
FUSION_MANIFEST = ROOT / "reports" / "evo" / f"{FUSION_STEM}.sampled_runtime_manifest.json"
FUSION_CONFIG = f"params/gold/fusion/{FUSION_STEM}.json"
SOURCE_COMPARISON = ROOT / "reports" / "evo" / "sampled_runtime_comparison_2021-2022-2023-2024_eval_2025"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def patch_fusion_manifest() -> None:
    payload = _load(FUSION_MANIFEST)
    payload["provenance"] = {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "eval_year": EVAL_YEAR,
        "race_start_target_lap": 3,
        "source_default_manifest_path": GOLD_MANIFEST,
        "static_fusion_config_path": FUSION_CONFIG,
        "train_years": TRAIN_YEARS,
    }
    _write(FUSION_MANIFEST, payload)


def materialize_rt_comparison() -> str:
    run_dt = datetime.now(timezone.utc).replace(microsecond=0)
    stem = make_artifact_slug("rt_comparison", run_dt, "2018thru2024")
    evo = ROOT / "reports" / "evo"
    summary_src = _load(SOURCE_COMPARISON.with_suffix(".summary.json"))
    details_src = _load(SOURCE_COMPARISON.with_suffix(".details.json"))

    run_config = {
        "train_years": TRAIN_YEARS,
        "eval_year": EVAL_YEAR,
        "race_start_target_lap": 3,
        "default_manifest": GOLD_MANIFEST,
        "trained_manifest": f"reports/evo/{FUSION_STEM}.sampled_runtime_manifest.json",
        "db_path_used": "data/f1_data_2025.db",
        "max_rounds_per_year": None,
        "race_name": [],
        "manifest_resolution": {
            "default": {
                "explicit_path_supplied": True,
                "resolved_path": GOLD_MANIFEST,
                "candidate_paths_checked": [],
                "status": "resolved",
            },
            "trained": {
                "explicit_path_supplied": True,
                "resolved_path": f"reports/evo/{FUSION_STEM}.sampled_runtime_manifest.json",
                "candidate_paths_checked": [],
                "status": "resolved",
            },
        },
    }

    created_at = run_dt.isoformat()
    for payload in (summary_src, details_src):
        payload["run_config"] = run_config
        payload["created_at"] = created_at
        payload.setdefault("source_run_created_at", created_at)
        payload.setdefault("summary_artifact_created_at", created_at)
        payload.setdefault("details_artifact_created_at", created_at)

    summary_path = evo / f"{stem}.summary.json"
    details_path = evo / f"{stem}.details.json"
    md_path = evo / f"{stem}.md"
    _write(summary_path, summary_src)
    _write(details_path, details_src)

    md_src = SOURCE_COMPARISON.with_suffix(".md")
    if md_src.exists():
        md_path.write_text(md_src.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        md_path.write_text(
            "\n".join(
                [
                    "# Sampled Runtime Default vs Trained Fusion Comparison",
                    "",
                    f"- Details JSON: `{details_path.relative_to(ROOT).as_posix()}`",
                    f"- Train years: {TRAIN_YEARS}",
                    f"- Eval year: {EVAL_YEAR}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    return stem


def main() -> int:
    patch_fusion_manifest()
    stem = materialize_rt_comparison()
    print(f"Patched provenance on {FUSION_MANIFEST.name}")
    print(f"Materialized rt_comparison artifacts: {stem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

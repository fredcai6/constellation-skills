"""Build a v4 sampled-runtime manifest for a LOSO heldout fold, fused with gold fusion.

INFERENCE glue (lives in .agent-work, not src/). It reuses the canonical assembler
(``assemble_sampled_runtime_manifest``) to point the manifest at the heldout_<Y> fold's
12 module bundles (trained WITHOUT season Y), then overlays the gold static-fusion
config's per-stage ``runtime_fusion`` blocks so the LOSO model is fused EXACTLY like the
promoted 2025 gold manifest. Only the module weights differ (LOSO fold vs full gold).

The gold fusion was trained on LOSO OOF rows spanning ALL train years (2018-2024); it
therefore structurally "saw" season Y's OOF metrics. Acceptable for a first pass (fusion
is a small set of precision scalars, not the per-event predictor); flagged as a follow-up
for strict per-season-holdout fusion in the report.

Usage:
    py .agent-work/multiseason-fantasy/build_loso_manifest.py --year <Y> --output <path>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.evo_predictor.pipeline_manifest_v4 import load_sampled_runtime_config
from src.evo_predictor.sampled_runtime_manifest_assembly import (
    assemble_sampled_runtime_manifest,
)

REPO = Path(__file__).resolve().parents[2]
GOLD_FUSION = REPO / "params/gold/fusion/fusion_260608_084626_2018thru2024.json"
REFERENCE_MANIFEST = REPO / "reports/evo/fusion_260608_084626_2018thru2024.sampled_runtime_manifest.json"
MODULE_NAMES = (
    "constructor_quali_power_from_race_weekend",
    "constructor_quali_power_from_recent_history",
    "constructor_race_power_from_race_weekend",
    "constructor_race_power_from_recent_history",
    "constructor_race_start_power_from_race_weekend",
    "constructor_race_start_power_from_recent_history",
    "driver_quali_power_from_race_weekend",
    "driver_quali_power_from_recent_history",
    "driver_race_power_from_race_weekend",
    "driver_race_power_from_recent_history",
    "driver_race_start_power_from_race_weekend",
    "driver_race_start_power_from_recent_history",
)


def build(year: int, output: Path) -> Path:
    fold_root = REPO / f"outputs/evo_runs/gold_module_training_cycle/loso_folds/heldout_{year}/modules"
    module_manifests = {
        name: str(fold_root / name / "latent_power_manifest.json") for name in MODULE_NAMES
    }
    missing = [n for n, p in module_manifests.items() if not Path(p).exists()]
    if missing:
        raise FileNotFoundError(f"heldout_{year}: missing module manifests {missing}")

    # 1) Assemble base manifest pointed at the LOSO fold (canonical assembler + validation).
    base_path = output.with_suffix(".base.json")
    assemble_sampled_runtime_manifest(
        module_manifests,
        output=base_path,
        n_samples=1000,
        seed=0,
        race_start_target_lap=3,
        quali_pace_anchor_enabled=True,
        quali_pace_anchor_alpha=0.5,
    )
    manifest = json.loads(base_path.read_text(encoding="utf-8"))

    # 2) Overlay the gold fusion config's runtime_fusion block per stage.
    fusion_cfg = json.loads(GOLD_FUSION.read_text(encoding="utf-8"))
    for task, stage in manifest["stages"].items():
        runtime_fusion = fusion_cfg["tasks"][task]["runtime_fusion"]
        # Safety: the fold's module set must match the gold fusion's fusion_order for this stage.
        if sorted(stage["fusion"]["fusion_order"]) != sorted(runtime_fusion["fusion_order"]):
            raise ValueError(
                f"stage {task!r}: module set mismatch between LOSO base "
                f"({stage['fusion']['fusion_order']}) and gold fusion "
                f"({runtime_fusion['fusion_order']})"
            )
        stage["fusion"] = json.loads(json.dumps(runtime_fusion))  # deep copy

    manifest["provenance"] = {
        "built_by": ".agent-work/multiseason-fantasy/build_loso_manifest.py",
        "heldout_year": year,
        "module_source": str(fold_root),
        "module_training_excludes_year": year,
        "fusion_source": str(GOLD_FUSION),
        "fusion_train_years": fusion_cfg.get("train_years"),
        "fusion_eval_year": fusion_cfg.get("eval_year"),
        "fusion_caveat": (
            "gold static fusion was trained on LOSO OOF spanning all train years and "
            "structurally saw this heldout year's OOF metrics; follow-up: strict "
            "per-season-holdout fusion."
        ),
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # 3) Validate the final manifest loads under the canonical config loader.
    load_sampled_runtime_config(output)
    return output


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    out = build(args.year, Path(args.output))
    print(f"LOSO manifest (heldout_{args.year}): {out}")


if __name__ == "__main__":
    main()

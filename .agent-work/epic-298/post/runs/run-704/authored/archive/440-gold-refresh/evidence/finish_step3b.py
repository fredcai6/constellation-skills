"""Step 3b finisher: build the trained manifest the CORRECT way for given slugs.

Combines the two fixes discovered in this run:
  1. Use the canonical fusion_training.write_trained_sampled_runtime_manifest overlay
     (preserves quali_pace_anchor; scripts/assemble_trained_sampled_runtime_manifest.py
     silently drops it — runbook gap #3).
  2. Write it under the FUSION slug name (pipeline_validation discovers the trained
     manifest by fusion slug) with the provenance block Step 3b requires.

Prereqs: materialize_runtime_bundles.py already ran (gold report manifest is portable).

Usage (repo root):
    py .agent-work/440-gold-refresh/evidence/finish_step3b.py --gold-slug gold_cycle_<...> --fusion-slug fusion_<...>
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from src.evo_predictor.fusion_training._train import write_trained_sampled_runtime_manifest

ap = argparse.ArgumentParser()
ap.add_argument("--gold-slug", required=True)
ap.add_argument("--fusion-slug", required=True)
args = ap.parse_args()

gold_manifest = Path(f"reports/evo/{args.gold_slug}.sampled_runtime_manifest.json")
fusion_config = Path(f"params/gold/fusion/{args.fusion_slug}.json")
output = Path(f"reports/evo/{args.fusion_slug}.sampled_runtime_manifest.json")

fusion_payload = json.loads(fusion_config.read_text(encoding="utf-8"))
write_trained_sampled_runtime_manifest(gold_manifest, fusion_payload, output=output)

payload = json.loads(output.read_text(encoding="utf-8"))
payload["provenance"] = {
    "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "eval_year": 2025,
    "race_start_target_lap": 3,
    "source_default_manifest_path": str(gold_manifest).replace("\\", "/"),
    "static_fusion_config_path": str(fusion_config).replace("\\", "/"),
    "train_years": [2018, 2019, 2020, 2021, 2022, 2023, 2024],
}
output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

txt = output.read_text(encoding="utf-8")
assert "quali_pace_anchor" in txt, "anchor missing"
assert "outputs" not in txt, "non-portable path leaked"
m = json.loads(txt)
for task in ("quali", "race", "race_start"):
    assert "fusion_order" in m["stages"][task]["fusion"], f"{task}: fusion not overlaid"
print("trained manifest written:", output, "- anchor present, portable, fusion overlaid, provenance set")

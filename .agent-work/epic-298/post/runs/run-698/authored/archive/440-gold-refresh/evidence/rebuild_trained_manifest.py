"""Rebuild the trained manifest the canonical way (gold manifest + fusion overlay + provenance).

Why: scripts/assemble_trained_sampled_runtime_manifest.py rebuilds stages from scratch and
SILENTLY DROPS the quali_pace_anchor block (active in the promoted gold per #335/PR437).
The canonical writer (fusion_training.write_trained_sampled_runtime_manifest) overlays the
fusion config onto the source gold manifest, preserving the anchor. This script does that
against the already-portable gold report manifest, then adds the provenance block the
runbook requires (matching the committed fusion_260608 form).

Run from repo root: py .agent-work/440-gold-refresh/evidence/rebuild_trained_manifest.py
"""
from __future__ import annotations

import json
from pathlib import Path

from src.evo_predictor.fusion_training._train import write_trained_sampled_runtime_manifest

GOLD_MANIFEST = Path("reports/evo/gold_cycle_260611_231027_2018thru2024.sampled_runtime_manifest.json")
FUSION_CONFIG = Path("params/gold/fusion/fusion_260612_000020_2018thru2024.json")
OUTPUT = Path("reports/evo/fusion_260612_000020_2018thru2024.sampled_runtime_manifest.json")

fusion_payload = json.loads(FUSION_CONFIG.read_text(encoding="utf-8"))
write_trained_sampled_runtime_manifest(GOLD_MANIFEST, fusion_payload, output=OUTPUT)

# Add the provenance block (Step 3b requirement; the canonical writer does not emit it).
payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
payload["provenance"] = {
    "created_at": "2026-06-12T00:01:26+00:00",
    "eval_year": 2025,
    "race_start_target_lap": 3,
    "source_default_manifest_path": str(GOLD_MANIFEST).replace("\\", "/"),
    "static_fusion_config_path": str(FUSION_CONFIG).replace("\\", "/"),
    "train_years": [2018, 2019, 2020, 2021, 2022, 2023, 2024],
}
OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

# Sanity: anchor present, paths portable, fusion overlaid.
txt = OUTPUT.read_text(encoding="utf-8")
assert "quali_pace_anchor" in txt, "anchor missing after rebuild"
assert "outputs" not in txt and "C:\\\\Programs" not in txt, "non-portable path leaked"
m = json.loads(txt)
for task in ("quali", "race", "race_start"):
    fusion = m["stages"][task]["fusion"]
    assert "fusion_order" in fusion, f"{task}: fusion not overlaid"
print("rebuilt", OUTPUT, "- anchor present, portable, fusion overlaid, provenance set")

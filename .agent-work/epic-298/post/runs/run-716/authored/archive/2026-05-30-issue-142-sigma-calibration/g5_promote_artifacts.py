#!/usr/bin/env python3
"""Promote G5 gold-cycle outputs to params/gold per artifact policy."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SLUG = "gold_cycle_260530_042533_2018thru2024"
OUTPUT_DIR = ROOT / "outputs/evo_runs/gold_module_training_cycle"
DEST_ROOT = ROOT / "params/gold/runtime_bundles" / SLUG
MODULES_SRC = OUTPUT_DIR / "modules"
SAMPLED_MANIFEST_SRC = OUTPUT_DIR / "sampled_runtime_manifest.json"
REPORT_MANIFEST = ROOT / "reports/evo" / f"{SLUG}.sampled_runtime_manifest.json"


def repo_rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("/", "\\")


def copy_module_bundle(module_name: str) -> str:
    src = MODULES_SRC / module_name
    dest = DEST_ROOT / "modules" / module_name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    manifest = dest / "latent_power_manifest.json"
    if not manifest.exists():
        raise FileNotFoundError(f"missing manifest after copy: {manifest}")
    return repo_rel(manifest)


def main() -> int:
    module_names = sorted(p.name for p in MODULES_SRC.iterdir() if p.is_dir())
    if len(module_names) != 12:
        raise SystemExit(f"expected 12 modules, found {len(module_names)}")

    DEST_ROOT.mkdir(parents=True, exist_ok=True)
    destination_manifests: dict[str, str] = {}
    source_manifests: dict[str, str] = {}
    for module_name in module_names:
        source_manifests[module_name] = str(
            (MODULES_SRC / module_name / "latent_power_manifest.json").resolve()
        )
        destination_manifests[module_name] = copy_module_bundle(module_name)

    if SAMPLED_MANIFEST_SRC.exists():
        REPORT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SAMPLED_MANIFEST_SRC, REPORT_MANIFEST)

    provenance = {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "slug": SLUG,
        "lambda_sigma_nll": 1.0,
        "pairwise_sigma_nll_enabled": True,
        "destination_module_manifest_paths": destination_manifests,
        "modules_materialized": module_names,
        "source_module_manifest_paths": source_manifests,
        "source_sampled_runtime_manifest": str(SAMPLED_MANIFEST_SRC.resolve()),
        "report_sampled_runtime_manifest": repo_rel(REPORT_MANIFEST) if REPORT_MANIFEST.exists() else None,
        "uncertainty_calibration": repo_rel(
            ROOT / "params/gold/uncertainty_calibration/unc_cal_260530_042533_2018thru2024.json"
        ),
        "gold_cycle_summary": repo_rel(ROOT / "reports/evo" / f"{SLUG}.summary.json"),
    }
    prov_path = DEST_ROOT / "provenance.json"
    prov_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    print(f"Promoted {len(module_names)} modules -> {DEST_ROOT}")
    print(f"provenance: {prov_path}")
    if REPORT_MANIFEST.exists():
        print(f"sampled_runtime_manifest copy: {REPORT_MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

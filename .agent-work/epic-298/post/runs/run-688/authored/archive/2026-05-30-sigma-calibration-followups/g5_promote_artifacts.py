#!/usr/bin/env python3
"""Promote G5 gold-cycle outputs to params/gold per artifact policy."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs/evo_runs/gold_module_training_cycle"
MODULES_SRC = OUTPUT_DIR / "modules"
SAMPLED_MANIFEST_SRC = OUTPUT_DIR / "sampled_runtime_manifest.json"


def repo_rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def copy_module_bundle(dest_root: Path, module_name: str) -> str:
    src = MODULES_SRC / module_name
    dest = dest_root / "modules" / module_name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    manifest = dest / "latent_power_manifest.json"
    if not manifest.exists():
        raise FileNotFoundError(f"missing manifest after copy: {manifest}")
    return repo_rel(manifest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True, help="gold_cycle slug")
    parser.add_argument("--unc-cal-slug", required=True, help="unc_cal slug from summary")
    args = parser.parse_args()

    slug = args.slug
    dest_root = ROOT / "params/gold/runtime_bundles" / slug
    report_manifest = ROOT / "reports/evo" / f"{slug}.sampled_runtime_manifest.json"
    unc_path = ROOT / "params/gold/uncertainty_calibration" / f"{args.unc_cal_slug}.json"

    module_names = sorted(p.name for p in MODULES_SRC.iterdir() if p.is_dir())
    if len(module_names) != 12:
        raise SystemExit(f"expected 12 modules, found {len(module_names)}")

    dest_root.mkdir(parents=True, exist_ok=True)
    destination_manifests: dict[str, str] = {}
    source_manifests: dict[str, str] = {}
    for module_name in module_names:
        source_manifests[module_name] = str(
            (MODULES_SRC / module_name / "latent_power_manifest.json").resolve()
        )
        destination_manifests[module_name] = copy_module_bundle(dest_root, module_name)

    if SAMPLED_MANIFEST_SRC.exists():
        report_manifest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SAMPLED_MANIFEST_SRC, report_manifest)

    provenance = {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "slug": slug,
        "lambda_sigma_nll": 1.0,
        "student_t_nu": 4.0,
        "student_t_nu_sigma": None,
        "pairwise_sigma_nll_enabled": True,
        "destination_module_manifest_paths": destination_manifests,
        "modules_materialized": module_names,
        "source_module_manifest_paths": source_manifests,
        "source_sampled_runtime_manifest": str(SAMPLED_MANIFEST_SRC.resolve()),
        "report_sampled_runtime_manifest": repo_rel(report_manifest) if report_manifest.exists() else None,
        "uncertainty_calibration": repo_rel(unc_path) if unc_path.exists() else None,
        "gold_cycle_summary": repo_rel(ROOT / "reports/evo" / f"{slug}.summary.json"),
    }
    prov_path = dest_root / "provenance.json"
    prov_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    print(f"Promoted {len(module_names)} modules -> {dest_root}")
    print(f"provenance: {prov_path}")
    if report_manifest.exists():
        print(f"sampled_runtime_manifest: {report_manifest}")
    if unc_path.exists():
        print(f"unc_cal (from cycle): {unc_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

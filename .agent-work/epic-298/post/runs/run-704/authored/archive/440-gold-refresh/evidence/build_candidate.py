"""Assemble params/gold_candidate from the fresh slugged refresh artifacts (gold lifecycle step 1).

Copies the new slugged artifact set into the candidate root in the layout
migrate_gold_to_constant_names.py expects, writes a pre-promotion gold_provenance.json,
then the caller runs:  py scripts/migrate_gold_to_constant_names.py --gold-root params/gold_candidate

Run from repo root: py .agent-work/440-gold-refresh/evidence/build_candidate.py
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

_ap = argparse.ArgumentParser()
_ap.add_argument("--gold-slug", required=True)
_ap.add_argument("--fusion-slug", required=True)
_args = _ap.parse_args()

REPO = Path(".").resolve()
GOLD_SLUG = _args.gold_slug
FUSION_SLUG = _args.fusion_slug
UNC_CAL = "unc_cal_" + GOLD_SLUG.removeprefix("gold_cycle_") + ".json"
TRAIN_YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
EVAL_YEAR = 2025

cand = REPO / "params" / "gold_candidate"
if cand.exists():
    raise SystemExit(f"refusing: {cand} already exists — remove it first if rebuilding")
cand.mkdir(parents=True)

# 1. runtime bundles (slugged; migrate flattens)
src_rb = REPO / "params/gold/runtime_bundles" / GOLD_SLUG
shutil.copytree(src_rb, cand / "runtime_bundles" / GOLD_SLUG)

# 2. fusion config (slugged; migrate renames to fusion.json)
(cand / "fusion").mkdir()
shutil.copy2(REPO / "params/gold/fusion" / f"{FUSION_SLUG}.json", cand / "fusion" / f"{FUSION_SLUG}.json")

# 3. uncertainty calibration (slugged; migrate renames to unc_cal.json)
(cand / "uncertainty_calibration").mkdir()
shutil.copy2(
    REPO / "params/gold/uncertainty_calibration" / UNC_CAL,
    cand / "uncertainty_calibration" / UNC_CAL,
)

# 4. compound priors — current pooled set (pre-ruling 1: priors are current; copy as-is)
shutil.copytree(REPO / "params/gold/compound_prior", cand / "compound_prior")

# 5. candidate sampled_runtime_manifest.json = the trained (fusion) manifest, with module
#    paths rewritten root-relative (live-gold form: runtime_bundles/<slug>/modules/...;
#    migrate then strips the slug).
trained = json.loads(
    (REPO / "reports/evo" / f"{FUSION_SLUG}.sampled_runtime_manifest.json").read_text(encoding="utf-8")
)
old_prefix = "..\\..\\params\\gold\\runtime_bundles\\"
mods = trained.get("modules")
assert isinstance(mods, dict), "trained manifest modules not a dict"
n = 0
for entry in mods.values():
    mp = entry.get("manifest_path")
    if isinstance(mp, str) and mp.startswith(old_prefix):
        entry["manifest_path"] = "runtime_bundles\\" + mp[len(old_prefix):]
        n += 1
assert n == 12, f"expected 12 module paths, rewrote {n}"
(cand / "sampled_runtime_manifest.json").write_text(
    json.dumps(trained, indent=2) + "\n", encoding="utf-8"
)

# 6. provenance (pre-promotion: promoted_* empty; backtest_evidence filled after multiseason run)
prov = {
    "slug": GOLD_SLUG,
    "schema_version": 1,
    "model_arch": "latent_power_v4",
    "train_years": TRAIN_YEARS,
    "eval_year": EVAL_YEAR,
    "created_at": (lambda s: f"20{s[0:2]}-{s[2:4]}-{s[4:6]}T{s[7:9]}:{s[9:11]}:{s[11:13]}Z")(
        GOLD_SLUG.removeprefix("gold_cycle_")
    ),
    "promoted_at": "",
    "promoted_by": "",
    "git_sha_at_promotion": "",
    "supersedes_slug": "",
    "manifest": "sampled_runtime_manifest.json",
    "fusion": "fusion/fusion.json",
    "backtest_evidence": {},
    "leakage_attestation": {"eval_year_excluded_from_train": True},
}
(cand / "gold_provenance.json").write_text(json.dumps(prov, indent=2) + "\n", encoding="utf-8")

print("candidate assembled at", cand)
for p in sorted(cand.iterdir()):
    print(" ", p.name)

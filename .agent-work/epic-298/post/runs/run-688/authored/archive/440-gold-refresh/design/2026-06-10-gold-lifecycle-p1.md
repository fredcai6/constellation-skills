# Gold Lifecycle P1 — Layout + Provenance + Validation Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the live committed gold to constant (slug-free) filenames, add a single `gold_provenance.json`, and add a `pipeline_validation` provenance gate that rejects stale/extra artifacts and `eval_year ∈ train_years` — keeping all validation green throughout.

**Architecture:** A new `gold_provenance` module owns the schema, the leakage invariant, and the "exact artifact set" check. A one-time, fixture-tested migration script renames the slugged June gold to constant names and rewrites the manifest's internal paths. `run_pipeline_validation.py` gains a `provenance` section and constant-name globs. Orphaned schema-v3 March files move to the gitignored archive.

**Tech Stack:** Python 3.14 (`py` launcher), pytest, stdlib `json`/`pathlib`/`re`. No new deps.

Spec: `docs/superpowers/specs/2026-06-10-gold-lifecycle-design.md` (§4 artifact set, §5 schema, §8 migration, §10 gate).

---

## File Structure

- **Create** `src/evo_predictor/gold_provenance.py` — schema (`GoldProvenance`), `load_provenance`, `assert_artifact_set`, `GOLD_*` constants. One responsibility: what gold *is* + its invariants.
- **Create** `tests/unit/evo_predictor/test_gold_provenance.py` — unit tests for the module.
- **Create** `scripts/migrate_gold_to_constant_names.py` — one-time migration (move slug dir up, rename fusion/unc_cal, rewrite manifest paths). Pure functions tested on a synthetic fixture.
- **Create** `tests/unit/scripts/test_migrate_gold_to_constant_names.py` — fixture test of the rewrite/move logic.
- **Create** `params/gold/gold_provenance.json` — the live June gold's provenance (committed data).
- **Modify** `params/gold/sampled_runtime_manifest.json` — internal module paths slug-free (via migration).
- **Move** `params/gold/runtime_bundles/gold_cycle_260608_043414_2018thru2024/*` → `params/gold/runtime_bundles/`; `fusion/fusion_*.json` → `fusion/fusion.json`; `uncertainty_calibration/unc_cal_*.json` → `.../unc_cal.json` (via migration).
- **Modify** `scripts/run_pipeline_validation.py` — constant-name globs + new `provenance` section.
- **Modify** `tests/unit/evo_predictor/test_pipeline_validation.py` — cover the provenance section.
- **Modify** slug-assuming consumers: `scripts/assemble_trained_sampled_runtime_manifest.py`, `scripts/accept_quali_anchor_420.py`, `scripts/export_pairwise_predictive_vs_retro.py`, `scripts/plot_predictive_vs_retro.py`, `scripts/report_predictive_retro_alignment.py`.
- **Modify** `.gitignore` — add `params/gold_candidate/`, `params/gold_archive/`.

---

## Task 1: `gold_provenance` module

**Files:**
- Create: `src/evo_predictor/gold_provenance.py`
- Test: `tests/unit/evo_predictor/test_gold_provenance.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/evo_predictor/test_gold_provenance.py
import json
from pathlib import Path

import pytest

from src.evo_predictor.gold_provenance import (
    GoldProvenance, ProvenanceError, load_provenance, assert_artifact_set,
)


def _write_min_gold(root: Path, *, eval_year=2025, train=(2018, 2019, 2020, 2021, 2022, 2023, 2024)):
    (root / "fusion").mkdir(parents=True)
    (root / "uncertainty_calibration").mkdir()
    (root / "runtime_bundles" / "driver_race_power_from_race_weekend").mkdir(parents=True)
    (root / "compound_prior" / "2025").mkdir(parents=True)
    (root / "fusion" / "fusion.json").write_text("{}", encoding="utf-8")
    (root / "uncertainty_calibration" / "unc_cal.json").write_text("{}", encoding="utf-8")
    (root / "sampled_runtime_manifest.json").write_text("{}", encoding="utf-8")
    (root / "gold_provenance.json").write_text(json.dumps({
        "slug": "gold_cycle_x", "train_years": list(train), "eval_year": eval_year,
    }), encoding="utf-8")


def test_load_provenance_ok(tmp_path):
    _write_min_gold(tmp_path)
    prov = load_provenance(tmp_path)
    assert prov.eval_year == 2025
    assert prov.train_years == (2018, 2019, 2020, 2021, 2022, 2023, 2024)


def test_load_provenance_missing_file(tmp_path):
    with pytest.raises(ProvenanceError, match="no gold_provenance.json"):
        load_provenance(tmp_path)


def test_eval_in_train_is_leakage(tmp_path):
    _write_min_gold(tmp_path, eval_year=2024)  # 2024 also in train -> leak
    with pytest.raises(ProvenanceError, match="leakage"):
        load_provenance(tmp_path)


def test_artifact_set_clean(tmp_path):
    _write_min_gold(tmp_path)
    assert assert_artifact_set(tmp_path) == []


def test_artifact_set_flags_stray(tmp_path):
    _write_min_gold(tmp_path)
    (tmp_path / "per_race_predictions").mkdir()
    problems = assert_artifact_set(tmp_path)
    assert any("per_race_predictions" in p for p in problems)
```

- [ ] **Step 2: Run to verify failure**

Run: `py -m pytest tests/unit/evo_predictor/test_gold_provenance.py -q`
Expected: FAIL (`ModuleNotFoundError: src.evo_predictor.gold_provenance`).

- [ ] **Step 3: Implement the module**

```python
# src/evo_predictor/gold_provenance.py
"""Gold provenance: the single in-repo record of what ``params/gold/`` is.

Stable, constant-named gold. See
docs/superpowers/specs/2026-06-10-gold-lifecycle-design.md (§4 artifact set, §5 schema).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

PROVENANCE_FILENAME = "gold_provenance.json"

GOLD_REQUIRED_FILES = (
    "gold_provenance.json",
    "sampled_runtime_manifest.json",
    "fusion/fusion.json",
    "uncertainty_calibration/unc_cal.json",
)
GOLD_REQUIRED_DIRS = ("runtime_bundles", "compound_prior")

# Top-level names allowed in a clean gold root. The first group is the live set;
# the second is load-bearing schema-v3 legacy still read by tooling (per_race_metrics
# -> pipeline_validation, command_meta -> summarize_training_history, config.json),
# tracked as a follow-up to migrate or regenerate.
_ALLOWED_TOP = {
    "gold_provenance.json", "sampled_runtime_manifest.json", "fusion",
    "uncertainty_calibration", "runtime_bundles", "compound_prior",
    "weights_best.json", "README.md",
    "per_race_metrics.json", "command_meta.json", "config.json",
}


class ProvenanceError(ValueError):
    """Missing/malformed provenance, or the eval-in-train leakage invariant fails."""


@dataclass(frozen=True)
class GoldProvenance:
    slug: str
    train_years: tuple[int, ...]
    eval_year: int
    schema_version: int = 1
    model_arch: str = "latent_power_v4"
    created_at: str = ""
    promoted_at: str = ""
    promoted_by: str = ""
    git_sha_at_promotion: str = ""
    supersedes_slug: str = ""
    backtest_evidence: Mapping[str, Any] = field(default_factory=dict)

    def assert_eval_excluded(self) -> None:
        if self.eval_year in self.train_years:
            raise ProvenanceError(
                f"leakage: eval_year {self.eval_year} is in train_years {self.train_years}"
            )


def load_provenance(gold_root: Path) -> GoldProvenance:
    path = Path(gold_root) / PROVENANCE_FILENAME
    if not path.exists():
        raise ProvenanceError(f"no {PROVENANCE_FILENAME} in {gold_root}")
    d = json.loads(path.read_text(encoding="utf-8"))
    try:
        prov = GoldProvenance(
            slug=str(d["slug"]),
            train_years=tuple(int(y) for y in d["train_years"]),
            eval_year=int(d["eval_year"]),
            schema_version=int(d.get("schema_version", 1)),
            model_arch=str(d.get("model_arch", "latent_power_v4")),
            created_at=str(d.get("created_at", "")),
            promoted_at=str(d.get("promoted_at", "")),
            promoted_by=str(d.get("promoted_by", "")),
            git_sha_at_promotion=str(d.get("git_sha_at_promotion", "")),
            supersedes_slug=str(d.get("supersedes_slug", "")),
            backtest_evidence=d.get("backtest_evidence", {}),
        )
    except KeyError as exc:
        raise ProvenanceError(f"{PROVENANCE_FILENAME} missing required field: {exc}") from exc
    prov.assert_eval_excluded()
    return prov


def assert_artifact_set(gold_root: Path) -> list[str]:
    """Return [] if ``gold_root`` is exactly the constant-named gold set, else problems.

    A stray ``per_race_predictions/`` (the March leak) or a leftover slugged file is
    reported here.
    """
    root = Path(gold_root)
    problems: list[str] = []
    for rel in GOLD_REQUIRED_FILES:
        if not (root / rel).is_file():
            problems.append(f"missing required file: {rel}")
    for rel in GOLD_REQUIRED_DIRS:
        if not (root / rel).is_dir():
            problems.append(f"missing required dir: {rel}/")
    for child in sorted(root.iterdir()):
        if child.name not in _ALLOWED_TOP:
            problems.append(f"unexpected gold artifact: {child.name}")
    return problems
```

- [ ] **Step 4: Run to verify pass**

Run: `py -m pytest tests/unit/evo_predictor/test_gold_provenance.py -q`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add src/evo_predictor/gold_provenance.py tests/unit/evo_predictor/test_gold_provenance.py
git commit -m "feat(gold): provenance module — schema, eval-not-in-train, artifact-set gate"
```

---

## Task 2: Migration script (rewrite/move logic, fixture-tested)

**Files:**
- Create: `scripts/migrate_gold_to_constant_names.py`
- Test: `tests/unit/scripts/test_migrate_gold_to_constant_names.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/scripts/test_migrate_gold_to_constant_names.py
import json
import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "migrate_gold", Path("scripts/migrate_gold_to_constant_names.py"))
migrate_gold = importlib.util.module_from_spec(_SPEC); _SPEC.loader.exec_module(migrate_gold)


def _slugged_gold(root: Path, slug="gold_cycle_260608_043414_2018thru2024",
                  fusion="fusion_260608_084626_2018thru2024.json",
                  unc="unc_cal_260608_043414_2018thru2024.json"):
    (root / "runtime_bundles" / slug / "modules" / "driver_race_power_from_race_weekend").mkdir(parents=True)
    (root / "fusion").mkdir(); (root / "uncertainty_calibration").mkdir()
    (root / "fusion" / fusion).write_text("{}", encoding="utf-8")
    (root / "uncertainty_calibration" / unc).write_text("{}", encoding="utf-8")
    (root / "sampled_runtime_manifest.json").write_text(json.dumps({
        "modules": {"driver_race_power_from_race_weekend": {
            "manifest_path": f"runtime_bundles\\\\{slug}\\\\modules\\\\driver_race_power_from_race_weekend\\\\latent_power_manifest.json"}}
    }), encoding="utf-8")
    return slug


def test_rewrite_manifest_paths_drops_slug():
    raw = {"modules": {"m": {"manifest_path":
        "runtime_bundles\\gold_cycle_260608_043414_2018thru2024\\modules\\m\\latent_power_manifest.json"}}}
    out = migrate_gold.rewrite_manifest_paths(raw)
    assert out["modules"]["m"]["manifest_path"] == "runtime_bundles/modules/m/latent_power_manifest.json"


def test_migrate_moves_and_renames(tmp_path):
    _slugged_gold(tmp_path)
    migrate_gold.migrate(tmp_path)
    assert (tmp_path / "fusion" / "fusion.json").is_file()
    assert (tmp_path / "uncertainty_calibration" / "unc_cal.json").is_file()
    assert (tmp_path / "runtime_bundles" / "modules" / "driver_race_power_from_race_weekend").is_dir()
    assert not list((tmp_path / "runtime_bundles").glob("gold_cycle_*"))
    man = json.loads((tmp_path / "sampled_runtime_manifest.json").read_text(encoding="utf-8"))
    assert "gold_cycle_" not in man["modules"]["driver_race_power_from_race_weekend"]["manifest_path"]
```

- [ ] **Step 2: Run to verify failure**

Run: `py -m pytest tests/unit/scripts/test_migrate_gold_to_constant_names.py -q`
Expected: FAIL (no `rewrite_manifest_paths` / `migrate`).

- [ ] **Step 3: Implement the script**

```python
# scripts/migrate_gold_to_constant_names.py
"""One-time migration: slugged live gold -> constant names (spec §8).

Idempotent-ish: safe to re-run; already-constant inputs are left alone. Operates on a
gold root (default params/gold). Use --dry-run to print the plan.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

_SLUG_IN_PATH = re.compile(r"runtime_bundles[\\/]gold_cycle_[^\\/]+[\\/]")


def rewrite_manifest_paths(manifest: dict) -> dict:
    """Replace ``runtime_bundles/<slug>/`` with ``runtime_bundles/`` in module paths,
    normalising backslashes to ``/``."""
    mods = manifest.get("modules")
    if isinstance(mods, dict):
        for entry in mods.values():
            if isinstance(entry, dict) and isinstance(entry.get("manifest_path"), str):
                p = _SLUG_IN_PATH.sub("runtime_bundles/", entry["manifest_path"])
                entry["manifest_path"] = p.replace("\\", "/")
    return manifest


def _rename_glob(d: Path, pattern: str, target: str) -> None:
    hits = sorted(d.glob(pattern))
    if not hits:
        return  # already migrated or absent
    if (d / target) in hits:
        return
    hits[0].rename(d / target)


def migrate(gold_root: Path) -> None:
    root = Path(gold_root)
    # 1. runtime_bundles/<slug>/* -> runtime_bundles/*
    rb = root / "runtime_bundles"
    slug_dirs = sorted(p for p in rb.glob("gold_cycle_*") if p.is_dir())
    for slug_dir in slug_dirs:
        for child in slug_dir.iterdir():
            dest = rb / child.name
            if dest.exists():
                shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
            child.rename(dest)
        slug_dir.rmdir()
    # 2. fusion_<slug>.json -> fusion.json ; unc_cal_<slug>.json -> unc_cal.json
    _rename_glob(root / "fusion", "fusion_*.json", "fusion.json")
    _rename_glob(root / "uncertainty_calibration", "unc_cal_*.json", "unc_cal.json")
    # 3. rewrite manifest internal paths
    man_path = root / "sampled_runtime_manifest.json"
    if man_path.is_file():
        man = json.loads(man_path.read_text(encoding="utf-8"))
        man_path.write_text(json.dumps(rewrite_manifest_paths(man), indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold-root", type=Path, default=Path("params/gold"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.dry_run:
        rb = args.gold_root / "runtime_bundles"
        print("slug dirs:", [p.name for p in rb.glob("gold_cycle_*")])
        print("fusion:", [p.name for p in (args.gold_root / "fusion").glob("fusion_*.json")])
        return 0
    migrate(args.gold_root)
    print(f"migrated {args.gold_root} to constant names")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run to verify pass**

Run: `py -m pytest tests/unit/scripts/test_migrate_gold_to_constant_names.py -q`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/migrate_gold_to_constant_names.py tests/unit/scripts/test_migrate_gold_to_constant_names.py
git commit -m "feat(gold): one-time slug->constant-name migration script (fixture-tested)"
```

---

## Task 3: pipeline_validation — constant-name globs + `provenance` section

**Files:**
- Modify: `scripts/run_pipeline_validation.py` (glob patterns near line 49–55; add a `provenance` section to the section runner)
- Test: `tests/unit/evo_predictor/test_pipeline_validation.py`

- [ ] **Step 1: Read the section runner** to match the existing pattern.

Run: `py -c "import re,io; s=open('scripts/run_pipeline_validation.py',encoding='utf-8').read(); print(s.count('def validate_'))"` then open the file and read how `_STATIC_CONFIG_PATTERNS` is consumed and how sections append results (the `@dataclass` Section/Result and the `--profile compact` section list).

- [ ] **Step 2: Update glob patterns to match constant names**

In `scripts/run_pipeline_validation.py`, change the slugged patterns to also match constant names (so the live, now-renamed gold is discovered):

```python
_STATIC_CONFIG_PATTERNS = [
    "params/gold/fusion/fusion.json",
    "params/gold/fusion/fusion_*.json",
]
_UNC_CAL_PATTERNS = [
    "params/gold/uncertainty_calibration/unc_cal.json",
    "params/gold/uncertainty_calibration/unc_cal_*.json",
]
```

- [ ] **Step 3: Write the failing test for the provenance section**

```python
# add to tests/unit/evo_predictor/test_pipeline_validation.py
def test_provenance_section_passes_clean_gold(tmp_path, monkeypatch):
    from scripts import run_pipeline_validation as rpv  # adjust import to how the module is loaded
    gold = tmp_path / "params" / "gold"
    # minimal clean gold (reuse the gold_provenance helper layout)
    from tests.unit.evo_predictor.test_gold_provenance import _write_min_gold
    _write_min_gold(gold)
    result = rpv.validate_provenance(gold_root=gold)
    assert result.passed, result.detail

def test_provenance_section_fails_eval_in_train(tmp_path):
    from scripts import run_pipeline_validation as rpv
    from tests.unit.evo_predictor.test_gold_provenance import _write_min_gold
    gold = tmp_path / "params" / "gold"
    _write_min_gold(gold, eval_year=2024)
    result = rpv.validate_provenance(gold_root=gold)
    assert not result.passed
```

(If the validator isn't import-friendly, adapt to its existing test harness — match how `test_pipeline_validation.py` already invokes sections.)

- [ ] **Step 4: Run to verify failure**

Run: `py -m pytest tests/unit/evo_predictor/test_pipeline_validation.py -q -k provenance`
Expected: FAIL (`validate_provenance` undefined).

- [ ] **Step 5: Implement `validate_provenance`** in `scripts/run_pipeline_validation.py`, matching the file's existing Section/Result dataclass shape:

```python
from src.evo_predictor.gold_provenance import (
    load_provenance, assert_artifact_set, ProvenanceError,
)

def validate_provenance(gold_root: Path = Path("params/gold")):
    """`provenance` section: gold_provenance present + eval∉train + exactly the artifact set."""
    problems = assert_artifact_set(gold_root)
    try:
        prov = load_provenance(gold_root)
    except ProvenanceError as exc:
        problems.append(str(exc))
        prov = None
    if prov is not None and list(prov.train_years) != CANONICAL_TRAIN_YEARS:
        problems.append(f"train_years {prov.train_years} != canonical {CANONICAL_TRAIN_YEARS}")
    if prov is not None and prov.eval_year != CANONICAL_EVAL_YEAR:
        problems.append(f"eval_year {prov.eval_year} != canonical {CANONICAL_EVAL_YEAR}")
    detail = "ok" if not problems else "; ".join(problems)
    return _Section("provenance", passed=not problems, detail=detail)  # use the file's actual result type
```

Wire `provenance` into the compact-profile section list alongside `gold`, `static_fusion`, etc.

- [ ] **Step 6: Run to verify pass**

Run: `py -m pytest tests/unit/evo_predictor/test_pipeline_validation.py -q`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add scripts/run_pipeline_validation.py tests/unit/evo_predictor/test_pipeline_validation.py
git commit -m "feat(gold): pipeline_validation provenance gate (eval-not-in-train + artifact set)"
```

---

## Task 4: Fix slug-assuming consumers

**Files (modify):** `scripts/assemble_trained_sampled_runtime_manifest.py`, `scripts/accept_quali_anchor_420.py`, `scripts/export_pairwise_predictive_vs_retro.py`, `scripts/plot_predictive_vs_retro.py`, `scripts/report_predictive_retro_alignment.py`

- [ ] **Step 1: Repoint the three "newest gold_cycle dir" discoverers** to the constant bundle root. Each has a helper like *"newest gold_cycle bundle directory in params/gold/runtime_bundles/"*. Replace the newest-slug-dir logic with the constant path:

```python
def _gold_bundle_root() -> Path:
    return Path("params/gold/runtime_bundles")  # constant; was: newest gold_cycle_* subdir
```

Update call sites that appended `/modules` under the slug dir to use `params/gold/runtime_bundles/modules/...` (the slug level is gone).

- [ ] **Step 2: Fix the hardcoded slug** in `scripts/accept_quali_anchor_420.py:56`:

```python
BUNDLE_NAME = ""  # constant-name gold: bundles live directly under params/gold/runtime_bundles/
```
and update its uses of `runtime_bundles/<BUNDLE_NAME>/` to `runtime_bundles/` (drop the segment).

- [ ] **Step 3: Fix the fusion glob** in `scripts/assemble_trained_sampled_runtime_manifest.py` (the `fusion_*_{descriptor}.json` pattern) to prefer the constant name:

```python
# prefer constant fusion.json; fall back to legacy slug glob
cand = Path("params/gold/fusion/fusion.json")
fusion_path = cand if cand.is_file() else sorted(Path("params/gold/fusion").glob(f"fusion_*_{_descriptor(train_years)}.json"))[-1]
```

- [ ] **Step 4: Verify nothing else references a slug**

Run: `grep -rn -E "gold_cycle_260608|fusion_260608|unc_cal_260608" --include=*.py src/ scripts/ tests/ | grep -v reports/evo | grep -v outputs/`
Expected: no output (the test fixtures in Task 2 build their own slugs; ignore those).

- [ ] **Step 5: Commit**

```bash
git add scripts/assemble_trained_sampled_runtime_manifest.py scripts/accept_quali_anchor_420.py scripts/export_pairwise_predictive_vs_retro.py scripts/plot_predictive_vs_retro.py scripts/report_predictive_retro_alignment.py
git commit -m "refactor(gold): point consumers at constant-name gold (drop slug discovery)"
```

---

## Task 5: Archive orphaned schema-v3 March files

**Files:** moves under `params/gold/` (git rm + local move to gitignored archive)

- [ ] **Step 1: Add gitignore entries** in `.gitignore`:

```
# Gold lifecycle: only params/gold/ (live) is committed
params/gold_candidate/
params/gold_archive/
```

- [ ] **Step 2: Enumerate current top-level gold entries and classify**

Run: `git ls-tree --name-only HEAD params/gold/`
Keep (live set + load-bearing legacy): `gold_provenance.json` (added Task 6), `sampled_runtime_manifest.json`, `fusion/`, `uncertainty_calibration/`, `runtime_bundles/`, `compound_prior/`, `weights_best.json`, `README.md`, `per_race_metrics.json`, `command_meta.json`, `config.json`.
Orphan candidates (verify no code refs first): `baseline_quali_map.json`, `baseline_race_de.json`, `metrics_all_races.json`, `metrics_gap_report.json`, `metrics_normal_only.json`, `race_baseline_latents.json`, `race_reliability_flags.json`, `artifact_lineage.json`, `fixed_split_running_log.jsonl`, `legacy_weights_2022.json`, `pipeline_manifest.json`, `stages/`.

- [ ] **Step 3: For each orphan candidate, confirm no code reference**

Run (example): `grep -rn "baseline_quali_map\|race_baseline_latents\|metrics_all_races\|pipeline_manifest" --include=*.py src/ scripts/ tests/ | grep -v test_gold_provenance`
Expected: no production references. Any file that IS referenced stays (add to `_ALLOWED_TOP` in `gold_provenance.py` with a `# load-bearing legacy` note instead of archiving).

- [ ] **Step 4: Move unreferenced orphans to the gitignored archive**

```bash
mkdir -p params/gold_archive/legacy-schema-v3
git mv params/gold/baseline_quali_map.json params/gold/baseline_race_de.json \
  params/gold/metrics_all_races.json params/gold/metrics_gap_report.json \
  params/gold/metrics_normal_only.json params/gold/race_baseline_latents.json \
  params/gold/race_reliability_flags.json params/gold/artifact_lineage.json \
  params/gold/fixed_split_running_log.jsonl params/gold/legacy_weights_2022.json \
  params/gold/pipeline_manifest.json params/gold_archive/legacy-schema-v3/
git mv params/gold/stages params/gold_archive/legacy-schema-v3/stages
```
(Drop any file from this list that Step 3 found referenced.)

- [ ] **Step 5: Commit**

```bash
git add .gitignore
git commit -m "chore(gold): gitignore candidate/archive; archive orphaned schema-v3 March files"
```

---

## Task 6: Run the real migration + write provenance + full validation green

**Files:** `params/gold/*` (data), `params/gold/gold_provenance.json` (create)

- [ ] **Step 1: Dry-run the migration**

Run: `py scripts/migrate_gold_to_constant_names.py --dry-run`
Expected: prints the one slug dir + the `fusion_*.json`.

- [ ] **Step 2: Run the real migration**

Run: `py scripts/migrate_gold_to_constant_names.py`
Expected: `migrated params/gold to constant names`.
Verify: `ls params/gold/fusion` shows `fusion.json`; `ls params/gold/runtime_bundles` shows the 12 module dirs (no `gold_cycle_*`); `grep -c gold_cycle_ params/gold/sampled_runtime_manifest.json` → `0`.

- [ ] **Step 3: Write the real `gold_provenance.json`**

```bash
py - <<'PY'
import json, subprocess
from pathlib import Path
sha = subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip()
prov = {
  "slug": "gold_cycle_260608_043414_2018thru2024",
  "schema_version": 1,
  "model_arch": "latent_power_v4",
  "train_years": [2018,2019,2020,2021,2022,2023,2024],
  "eval_year": 2025,
  "created_at": "2026-06-08T04:34:14Z",
  "promoted_at": "2026-06-10T00:00:00Z",
  "promoted_by": "fredcai6",
  "git_sha_at_promotion": sha,
  "supersedes_slug": "",
  "manifest": "sampled_runtime_manifest.json",
  "fusion": "fusion/fusion.json",
  "backtest_evidence": {
    "multiseason_fantasy": {"2022":831,"2023":963,"2024":835,"2025":849},
    "human_reference": {"2022":739,"2023":632,"2024":615,"2025":711},
    "report": "reports/walkforward/multiseason_fantasy.json"
  },
  "leakage_attestation": {"eval_year_excluded_from_train": True}
}
Path("params/gold/gold_provenance.json").write_text(json.dumps(prov, indent=2)+"\n", encoding="utf-8")
print("wrote gold_provenance.json")
PY
```

- [ ] **Step 4: Full pipeline validation must be green**

Run: `py scripts/run_pipeline_validation.py --profile compact`
Expected: all sections (incl. new `provenance`) `pass`. If `manifest_portability` or `report_alignment` fail, fix the manifest paths the migration produced (they must be repo-relative, slug-free) and re-run.

- [ ] **Step 5: Run the broader gold/fantasy test surface**

Run: `py -m pytest tests/unit/evo_predictor/ tests/unit/scripts/ tests/unit/fantasy_scoring/ -q`
Expected: PASS.

- [ ] **Step 6: Commit the migrated gold**

```bash
git add params/gold
git commit -m "feat(gold): migrate live June gold to constant names + gold_provenance.json"
```

---

## Self-Review

- **Spec coverage:** §4 artifact set → Task 1 (`assert_artifact_set`) + Task 5/6. §5 schema → Task 1 + Task 6 Step 3. §8 migration → Tasks 2/4/6. §10 validation gate → Task 3. §3 gitignore → Task 5. (P2 promote/guard, P3 multi-season, P4 runbook are out of scope for P1, by design.)
- **Placeholder scan:** the only intentionally-deferred spot is "match the file's actual `_Section`/Result type" in Task 3 Step 5 — flagged because it depends on reading the validator's existing dataclass at execution; the logic and wiring are fully specified.
- **Type consistency:** `GoldProvenance`, `load_provenance`, `assert_artifact_set`, `rewrite_manifest_paths`, `migrate`, `validate_provenance` names are used consistently across tasks; `_ALLOWED_TOP` is the single source for the allowlist referenced by Task 5 Step 3.

# Student-t Phase 1b-wire: Live Baseline Harness — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement task-by-task. Steps use checkbox (`- [ ]`) syntax. The controller (not a subagent) runs the live-pipeline smoke + full baseline in Task 5.

**Goal:** Wire the Phase 1b-core dual-reference calibration to the live eval pipeline: auto-discover the latest gold-cycle bundle, extract per-task `(mu, sigma, target_mu)` for the held-out eval year, score current-Gaussian vs Student-t per task, and emit a baseline calibration report artifact.

**Architecture:** New module `src/calibration/harness.py` with (a) pure helpers — bundle discovery, eval-year inference, pair cleaning, report assembly, JSON serialization — and (b) one heavy `extract_task_arrays` that loads a trained module and runs `predict_pairwise` over DB-built eval batches. A thin CLI (`src/calibration/run.py` + `__main__.py`) ties discovery → extraction → `build_baseline_report` → write `reports/calibration/`. Pure parts are TDD-tested; the extractor's testable core (`_clean_pairs`) is unit-tested and the end-to-end run is validated live by the controller.

**Tech Stack:** Python 3.11, numpy, torch, scipy, pytest. Python is `py`. Pyright basic. DB is the single source of data — no FastF1.

**Spec:** `docs/superpowers/specs/2026-05-31-student-t-migration-design.md` (Phase 1 "measure first"). Builds on Phase 1b-core `src/calibration/baseline.py::evaluate_task_calibration`.

**Integration map (verified):**
- Load module: `load_latent_power_module_bundle(dir)` → `.module` (`src/evo_predictor/latent_power_bundle.py:88`).
- Adapter: `get_training_adapter(module_name)` → `.task`, `.entity_scope` (`module_training_orchestration.py:165`).
- Build batches: `build_labeled_batches_for_module(name, *, years=[year], db_by_year={year: DatabaseManager(...)})` → `tuple[RuntimePairBatchResult, ...]` (`module_training_orchestration.py:297`).
- Join retro: `_join_retro_results(batches, *, task, entity_scope, retro_root)` (`src/evo_predictor/run.py:328`).
- Per pair: `result.batch` → `PairBatch` with `.target_mu` (`Optional`), `module.predict_pairwise(batch)` → `PairwiseOutput.mu/.sigma`; convert via `.detach().cpu().numpy()` under `torch.no_grad()`.
- Module names: `list_modules()` (`src/latent_power/modules.py`); 12 trainable.
- `nu_loss` = bundle provenance `student_t_nu` (4.0). Eval year = final train year + 1 (slug `...thru2024` → 2025).

---

## File Structure

- **Create `src/calibration/harness.py`** — `discover_latest_bundle`, `bundle_nu_loss`, `eval_year_for_bundle`, `_clean_pairs`, `extract_task_arrays`, `build_baseline_report`, `write_baseline_report`.
- **Create `src/calibration/run.py`** — argparse `baseline` subcommand.
- **Create `src/calibration/__main__.py`** — `python -m src.calibration` entry.
- **Create `tests/unit/calibration/test_harness.py`** — pure-helper TDD.

`src/calibration/__init__.py` is NOT extended (the harness is invoked via CLI / explicit import, keeping the scoring API surface clean).

---

## Task 1: Bundle discovery, nu_loss, and eval-year inference

**Files:**
- Create: `src/calibration/harness.py`
- Create: `tests/unit/calibration/test_harness.py`

- [ ] **Step 1: Write failing tests**

Create `tests/unit/calibration/test_harness.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from src.calibration.harness import (
    bundle_nu_loss,
    discover_latest_bundle,
    eval_year_for_bundle,
)


def test_discover_latest_bundle_picks_newest_by_name(tmp_path: Path) -> None:
    root = tmp_path / "runtime_bundles"
    root.mkdir()
    (root / "gold_cycle_260101_000000_2018thru2024").mkdir()
    (root / "gold_cycle_260530_152746_2018thru2024").mkdir()
    (root / "gold_cycle_260315_000000_2018thru2024").mkdir()
    latest = discover_latest_bundle(root)
    assert latest.name == "gold_cycle_260530_152746_2018thru2024"


def test_discover_latest_bundle_errors_when_empty(tmp_path: Path) -> None:
    root = tmp_path / "runtime_bundles"
    root.mkdir()
    with pytest.raises(FileNotFoundError, match="no gold-cycle bundle"):
        discover_latest_bundle(root)


def test_eval_year_for_bundle_is_final_train_year_plus_one(tmp_path: Path) -> None:
    bundle = tmp_path / "gold_cycle_260530_152746_2018thru2024"
    bundle.mkdir()
    assert eval_year_for_bundle(bundle) == 2025


def test_eval_year_for_bundle_handles_single_year_slug(tmp_path: Path) -> None:
    bundle = tmp_path / "gold_cycle_260517_034150_2021thru2024"
    bundle.mkdir()
    assert eval_year_for_bundle(bundle) == 2025


def test_eval_year_for_bundle_rejects_unparseable_slug(tmp_path: Path) -> None:
    bundle = tmp_path / "weird_bundle_name"
    bundle.mkdir()
    with pytest.raises(ValueError, match="cannot infer eval year"):
        eval_year_for_bundle(bundle)


def test_bundle_nu_loss_reads_provenance(tmp_path: Path) -> None:
    bundle = tmp_path / "gold_cycle_x"
    bundle.mkdir()
    (bundle / "provenance.json").write_text(json.dumps({"student_t_nu": 4.0}))
    assert bundle_nu_loss(bundle) == 4.0


def test_bundle_nu_loss_defaults_when_missing(tmp_path: Path) -> None:
    bundle = tmp_path / "gold_cycle_y"
    bundle.mkdir()
    (bundle / "provenance.json").write_text(json.dumps({}))
    assert bundle_nu_loss(bundle) == 4.0
```

- [ ] **Step 2: Run to verify they fail**

Run: `py -m pytest tests/unit/calibration/test_harness.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.calibration.harness'`.

- [ ] **Step 3: Implement the discovery/inference helpers**

Create `src/calibration/harness.py`:

```python
"""Live baseline harness: wire the dual-reference calibration to trained bundles.

Discovers the latest gold-cycle bundle, extracts per-task (mu, sigma, target_mu)
for the held-out eval year, scores Gaussian-vs-Student-t per task, and writes a
baseline calibration report. The pure helpers here are unit-tested; the live
extraction is validated by running the CLI against real artifacts.

See docs/superpowers/specs/2026-05-31-student-t-migration-design.md.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

DEFAULT_BUNDLE_ROOT = Path("params/gold/runtime_bundles")
DEFAULT_DB_ROOT = Path("data")
DEFAULT_RETRO_ROOT = Path("params/retro_truth")
DEFAULT_REPORT_ROOT = Path("reports/calibration")
DEFAULT_NU_LOSS = 4.0


def discover_latest_bundle(root: Path = DEFAULT_BUNDLE_ROOT) -> Path:
    """Return the newest ``gold_cycle_*`` bundle dir under ``root`` (lexical max).

    Bundle slugs embed a ``YYMMDD_HHMMSS`` stamp, so lexical max == newest.
    """
    candidates = sorted(
        p for p in root.glob("gold_cycle_*") if p.is_dir()
    )
    if not candidates:
        raise FileNotFoundError(f"no gold-cycle bundle found under {root}")
    return candidates[-1]


def eval_year_for_bundle(bundle_dir: Path) -> int:
    """Infer the held-out eval year as (final training year + 1).

    Bundle slugs encode the training span as ``...<start>thru<end>``; the eval
    year is the season after ``<end>``.
    """
    match = re.search(r"thru(\d{4})", bundle_dir.name)
    if match is None:
        raise ValueError(f"cannot infer eval year from bundle name {bundle_dir.name!r}")
    return int(match.group(1)) + 1


def bundle_nu_loss(bundle_dir: Path) -> float:
    """Read the aleatoric loss nu (``student_t_nu``) from bundle provenance."""
    provenance = bundle_dir / "provenance.json"
    if not provenance.exists():
        return DEFAULT_NU_LOSS
    data = json.loads(provenance.read_text())
    value = data.get("student_t_nu")
    if not isinstance(value, (int, float)):
        return DEFAULT_NU_LOSS
    return float(value)
```

- [ ] **Step 4: Run to verify pass**

Run: `py -m pytest tests/unit/calibration/test_harness.py -v`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```bash
git add src/calibration/harness.py tests/unit/calibration/test_harness.py
git commit -m "feat(calibration): add bundle discovery + eval-year/nu_loss inference"
```

---

## Task 2: `_clean_pairs` and `build_baseline_report`

**Files:**
- Modify: `src/calibration/harness.py`
- Test: `tests/unit/calibration/test_harness.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/unit/calibration/test_harness.py`:

```python
def test_clean_pairs_drops_none_target_and_non_finite() -> None:
    from src.calibration.harness import _clean_pairs

    mu = np.array([0.0, 1.0, 2.0, 3.0])
    sigma = np.array([1.0, 1.0, 0.0, 1.0])      # third has bad sigma
    target = np.array([0.5, np.nan, 1.0, 2.0])  # second is non-finite
    cmu, csigma, ctarget = _clean_pairs(mu, sigma, target)
    # only rows 0 and 3 survive (row1 nan target, row2 sigma<=0)
    np.testing.assert_array_equal(cmu, [0.0, 3.0])
    np.testing.assert_array_equal(csigma, [1.0, 1.0])
    np.testing.assert_array_equal(ctarget, [0.5, 2.0])


def test_clean_pairs_returns_empty_when_target_is_none() -> None:
    from src.calibration.harness import _clean_pairs

    mu = np.array([0.0, 1.0])
    sigma = np.array([1.0, 1.0])
    cmu, csigma, ctarget = _clean_pairs(mu, sigma, None)
    assert cmu.shape == (0,) and csigma.shape == (0,) and ctarget.shape == (0,)


def test_build_baseline_report_scores_each_task() -> None:
    from src.calibration.harness import build_baseline_report
    from src.common.student_t import FormulaRule

    rng = np.random.default_rng(0)
    n = 4000
    mu = rng.normal(0.0, 1.0, size=n)
    sigma = np.ones(n)
    target = rng.normal(mu, sigma)
    arrays_by_task = {"driver_race": (mu, sigma, target)}
    report = build_baseline_report(
        arrays_by_task,
        nu_loss=4.0,
        rule=FormulaRule(),
        n_eff=1e6,
        levels=(0.9,),
        n_crps_samples=100,
        seed=1,
    )
    assert report["nu_loss"] == 4.0
    task = report["tasks"]["driver_race"]
    assert task["n"] == n
    assert task["gaussian"]["coverage"]["0.9"] == pytest.approx(0.9, abs=0.03)
    assert task["student_t"]["coverage"]["0.9"] > task["gaussian"]["coverage"]["0.9"]
    assert "p95" in task["r_over_sigma"]


def test_build_baseline_report_skips_empty_tasks() -> None:
    from src.calibration.harness import build_baseline_report
    from src.common.student_t import FormulaRule

    empty = (np.array([]), np.array([]), np.array([]))
    report = build_baseline_report(
        {"driver_race": empty}, nu_loss=4.0, rule=FormulaRule(), n_eff=1e6
    )
    assert report["tasks"]["driver_race"]["skipped"] == "no_labeled_pairs"
```

- [ ] **Step 2: Run to verify they fail**

Run: `py -m pytest tests/unit/calibration/test_harness.py -k "clean_pairs or build_baseline_report" -v`
Expected: FAIL — names not defined.

- [ ] **Step 3: Implement**

Add to the imports at the top of `src/calibration/harness.py` (below `from pathlib import Path`):

```python
from typing import Mapping, Sequence

import numpy as np

from src.calibration.baseline import evaluate_task_calibration
from src.common.student_t import TailRule
```

Append to `src/calibration/harness.py`:

```python
def _clean_pairs(
    mu: np.ndarray, sigma: np.ndarray, target: np.ndarray | None
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Drop pairs with no/Non-finite target or non-positive/non-finite sigma.

    Phase 1a scorers reject non-finite actuals by design; this is where the
    ``target_mu is None`` events and any numerical junk are filtered out.
    """
    if target is None:
        empty = np.array([], dtype=float)
        return empty, empty.copy(), empty.copy()
    mu = np.asarray(mu, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    target = np.asarray(target, dtype=float)
    keep = (
        np.isfinite(mu)
        & np.isfinite(sigma)
        & np.isfinite(target)
        & (sigma > 0.0)
    )
    return mu[keep], sigma[keep], target[keep]


def build_baseline_report(
    arrays_by_task: Mapping[str, tuple[np.ndarray, np.ndarray, np.ndarray | None]],
    *,
    nu_loss: float,
    rule: TailRule,
    n_eff: float,
    levels: Sequence[float] = (0.5, 0.8, 0.9, 0.95),
    n_crps_samples: int = 200,
    seed: int = 0,
) -> dict:
    """Assemble a JSON-serializable baseline report from per-task arrays.

    Each task is scored under the current Gaussian assumption and a Student-t
    reference. Tasks with no labeled pairs after cleaning are recorded as skipped.
    """
    tasks: dict[str, dict] = {}
    for task, (mu, sigma, target) in arrays_by_task.items():
        cmu, csigma, ctarget = _clean_pairs(mu, sigma, target)
        if cmu.shape[0] == 0:
            tasks[task] = {"skipped": "no_labeled_pairs", "n": 0}
            continue
        result = evaluate_task_calibration(
            task,
            cmu, csigma, ctarget,
            nu_loss=nu_loss, rule=rule, n_eff=n_eff,
            levels=levels, n_crps_samples=n_crps_samples, seed=seed,
        )
        tasks[task] = {
            "n": result.n,
            "gaussian": _summary_to_dict(result.gaussian),
            "student_t": _summary_to_dict(result.student_t),
            "r_over_sigma": dict(result.r_over_sigma),
        }
    return {"nu_loss": float(nu_loss), "n_eff": float(n_eff), "tasks": tasks}


def _summary_to_dict(summary: object) -> dict:
    """Serialize a CalibrationSummary (coverage keys -> strings for JSON)."""
    return {
        "n": getattr(summary, "n"),
        "coverage": {str(k): v for k, v in getattr(summary, "coverage").items()},
        "pit_mean": getattr(summary, "pit_mean"),
        "pit_var": getattr(summary, "pit_var"),
        "crps": getattr(summary, "crps"),
    }
```

- [ ] **Step 4: Run to verify pass**

Run: `py -m pytest tests/unit/calibration/test_harness.py -v`
Expected: PASS (Task 1 + Task 2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/calibration/harness.py tests/unit/calibration/test_harness.py
git commit -m "feat(calibration): add pair cleaning + baseline report assembly"
```

---

## Task 3: `extract_task_arrays` + `write_baseline_report` (live extraction)

**Files:**
- Modify: `src/calibration/harness.py`
- Test: `tests/unit/calibration/test_harness.py`

- [ ] **Step 1: Add a test for the serialization helper (pure) only**

The live `extract_task_arrays` is validated by the controller's smoke run (Task 5), not unit tests (it needs torch + DB + bundle). Add a test only for `write_baseline_report`. Append to `tests/unit/calibration/test_harness.py`:

```python
def test_write_baseline_report_writes_json(tmp_path: Path) -> None:
    from src.calibration.harness import write_baseline_report

    report = {"nu_loss": 4.0, "tasks": {"driver_race": {"n": 10}}}
    out = write_baseline_report(report, out_dir=tmp_path, slug="gold_x", eval_year=2025)
    assert out.exists()
    loaded = json.loads(out.read_text())
    assert loaded["tasks"]["driver_race"]["n"] == 10
    assert "gold_x" in out.name and "2025" in out.name
```

- [ ] **Step 2: Run to verify it fails**

Run: `py -m pytest tests/unit/calibration/test_harness.py -k write_baseline_report -v`
Expected: FAIL — `cannot import name 'write_baseline_report'`.

- [ ] **Step 3: Implement extraction + writer**

Add to the top imports of `src/calibration/harness.py`:

```python
import torch

from src.data.database import DatabaseManager
from src.evo_predictor.latent_power_bundle import load_latent_power_module_bundle
from src.evo_predictor.module_training_orchestration import (
    build_labeled_batches_for_module,
    get_training_adapter,
)
from src.evo_predictor.run import _join_retro_results
```

Append to `src/calibration/harness.py`:

```python
def extract_task_arrays(
    module_name: str,
    *,
    bundle_dir: Path,
    eval_year: int,
    db_root: Path = DEFAULT_DB_ROOT,
    retro_root: Path = DEFAULT_RETRO_ROOT,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """Run the trained module over the eval-year batches and return aligned
    per-pair (mu, sigma, target_mu). target_mu is None if no retro labels joined.

    Heavy: loads a checkpoint and runs torch inference over DB-built batches.
    """
    module_dir = bundle_dir / "modules" / module_name
    bundle = load_latent_power_module_bundle(module_dir)
    module = bundle.module
    adapter = get_training_adapter(module_name)

    db = DatabaseManager(db_path=str(db_root / f"f1_data_{eval_year}.db"))
    batches = build_labeled_batches_for_module(
        module_name, years=[eval_year], db_by_year={eval_year: db}
    )
    if retro_root.exists():
        batches = _join_retro_results(
            batches, task=adapter.task, entity_scope=adapter.entity_scope,
            retro_root=str(retro_root),
        )

    mus: list[np.ndarray] = []
    sigmas: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    any_target = False
    with torch.no_grad():
        for result in batches:
            batch = result.batch
            if batch is None:
                continue
            pairwise = module.predict_pairwise(batch)
            mus.append(pairwise.mu.detach().cpu().numpy())
            sigmas.append(pairwise.sigma.detach().cpu().numpy())
            if batch.target_mu is not None:
                any_target = True
                targets.append(batch.target_mu.detach().cpu().numpy())
            else:
                targets.append(np.full(pairwise.mu.shape[0], np.nan))

    if not mus:
        empty = np.array([], dtype=float)
        return empty, empty.copy(), (empty.copy() if any_target else None)
    mu = np.concatenate(mus)
    sigma = np.concatenate(sigmas)
    target = np.concatenate(targets) if any_target else None
    return mu, sigma, target


def write_baseline_report(
    report: dict, *, out_dir: Path, slug: str, eval_year: int
) -> Path:
    """Write the report dict to ``out_dir`` as JSON; return the path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"baseline_{slug}_eval{eval_year}.json"
    out.write_text(json.dumps(report, indent=2))
    return out
```

- [ ] **Step 4: Run to verify the pure test passes**

Run: `py -m pytest tests/unit/calibration/test_harness.py -v`
Expected: PASS (all unit tests; `extract_task_arrays` has no unit test by design).

- [ ] **Step 5: Commit**

```bash
git add src/calibration/harness.py tests/unit/calibration/test_harness.py
git commit -m "feat(calibration): add live per-task array extraction + report writer"
```

---

## Task 4: CLI entrypoint

**Files:**
- Create: `src/calibration/run.py`
- Create: `src/calibration/__main__.py`

- [ ] **Step 1: Implement the CLI (no unit test; exercised live in Task 5)**

Create `src/calibration/run.py`:

```python
"""CLI for the calibration baseline harness."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from src.calibration.harness import (
    DEFAULT_BUNDLE_ROOT,
    DEFAULT_REPORT_ROOT,
    build_baseline_report,
    bundle_nu_loss,
    discover_latest_bundle,
    eval_year_for_bundle,
    extract_task_arrays,
    write_baseline_report,
)
from src.common.student_t import FormulaRule
from src.latent_power.modules import list_modules


def cmd_baseline(args: argparse.Namespace) -> int:
    bundle_dir = (
        Path(args.bundle) if args.bundle else discover_latest_bundle(DEFAULT_BUNDLE_ROOT)
    )
    eval_year = int(args.eval_year) if args.eval_year else eval_year_for_bundle(bundle_dir)
    nu_loss = bundle_nu_loss(bundle_dir)
    module_names = list(args.modules) if args.modules else list(list_modules())

    print(f"bundle={bundle_dir.name} eval_year={eval_year} nu_loss={nu_loss}")
    arrays_by_task: dict = {}
    for name in module_names:
        module_dir = bundle_dir / "modules" / name
        if not module_dir.exists():
            print(f"  skip {name}: not in bundle")
            continue
        print(f"  extracting {name} ...")
        arrays_by_task[name] = extract_task_arrays(
            name, bundle_dir=bundle_dir, eval_year=eval_year
        )

    report = build_baseline_report(
        arrays_by_task,
        nu_loss=nu_loss,
        rule=FormulaRule(),
        n_eff=float(args.n_eff),
        n_crps_samples=int(args.n_crps_samples),
        seed=int(args.seed),
    )
    out = write_baseline_report(
        report, out_dir=DEFAULT_REPORT_ROOT, slug=bundle_dir.name, eval_year=eval_year
    )
    print(f"wrote {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Student-t calibration baseline harness")
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("baseline", help="Run the per-task calibration baseline")
    b.add_argument("--bundle", default=None, help="Bundle dir (default: latest)")
    b.add_argument("--eval-year", default=None, help="Eval year (default: inferred)")
    b.add_argument("--modules", nargs="+", default=None, help="Module names (default: all)")
    b.add_argument("--n-eff", default=1e6, help="Uniform n_eff for the baseline")
    b.add_argument("--n-crps-samples", default=200, help="Student-t CRPS samples per pair")
    b.add_argument("--seed", default=0, help="RNG seed for Student-t CRPS")
    b.set_defaults(func=cmd_baseline)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
```

Create `src/calibration/__main__.py`:

```python
"""Run the calibration harness as ``python -m src.calibration``."""

from src.calibration.run import main

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Verify the CLI parses (no pipeline run yet)**

Run: `py -m src.calibration baseline --help`
Expected: prints the subcommand help without error.

- [ ] **Step 3: Commit**

```bash
git add src/calibration/run.py src/calibration/__main__.py
git commit -m "feat(calibration): add baseline harness CLI"
```

---

## Task 5: Controller-driven live validation (NOT a subagent task)

The controller runs these against real artifacts and iterates on any real-world data issues. Do not delegate.

- [ ] **Step 1: Smoke one fast module** — `py -m src.calibration baseline --modules driver_race_power_from_recent_history`. Confirm it extracts, scores, and writes a report with finite coverage/CRPS for that task. Fix any extraction issues (field names, batch shapes, retro path) before scaling.
- [ ] **Step 2: Full run** — `py -m src.calibration baseline` over all 12 modules. Inspect the report: which tasks show Gaussian under-coverage / high `r/sigma` p99 (fat tails the current world misses), and whether Student-t already improves coverage/CRPS.
- [ ] **Step 3: Commit the generated baseline report** under `reports/calibration/` and summarize the per-task findings (this is the Phase 1 deliverable: the before-picture every later phase is judged against).

---

## Self-Review Notes (for the implementer)

- **Spec coverage:** Produces the Phase 1 baseline — current-Gaussian vs Student-t coverage/CRPS + `r/sigma` dashboard per task, over the held-out eval year of the latest bundle. The DB is the only data source; `target_mu is None` events are filtered in `_clean_pairs`.
- **Testable vs live split:** discovery, eval-year, `nu_loss`, `_clean_pairs`, `build_baseline_report`, `write_baseline_report` are unit-tested; `extract_task_arrays` and the CLI are validated by the controller's live run (Task 5).
- **Type consistency:** `extract_task_arrays(module_name, *, bundle_dir, eval_year, db_root, retro_root)`, `build_baseline_report(arrays_by_task, *, nu_loss, rule, n_eff, levels, n_crps_samples, seed)`, `write_baseline_report(report, *, out_dir, slug, eval_year)`. Report dict shape: `{nu_loss, n_eff, tasks: {name: {n, gaussian, student_t, r_over_sigma} | {skipped, n}}}`.
- **Pyright:** explicit return types, `from __future__ import annotations`.

# Student-t Phase 1b-core: Per-Task Baseline Report — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the pure per-task calibration report core: given a task's per-prediction `(mu, sigma, target)` arrays, score the **current Gaussian assumption** and a **Student-t reference** on identical data, and compute the `r/sigma` tail dashboard — so a later wiring step can produce a baseline before/after picture. No DB, no model, no behavior change to existing code.

**Architecture:** A new module `src/calibration/baseline.py` building on Phase 1a's `scoring.py` and Phase 0's `student_t.py`. For each task it wraps predictions two ways — `scipy.stats.norm(mu_i, sigma_i)` (the current Gaussian world) and `predictive_t(mu_i, sigma_i, n_eff, nu_loss, rule)` (Student-t) — scores both via `summarize_calibration`, and reports `|r/sigma|` quantiles. Gaussian CRPS uses the exact closed form; Student-t CRPS uses the sample-based estimator over `PredictiveT.sample`. Pure functions over numpy arrays; fully unit-testable with synthetic data.

**Tech Stack:** Python 3.11, numpy, scipy.stats, pytest. Python is `py`; tests via `py -m pytest`. Pyright `basic` — explicit return types, `from __future__ import annotations`.

**Spec:** `docs/superpowers/specs/2026-05-31-student-t-migration-design.md` (Phase 1 "measure first": coverage gate + CRPS score + `r/sigma` dashboard).

**Roadmap context:** Phase 0 (done) = `student_t.py`. Phase 1a (done) = `scoring.py`. **Phase 1b-core (this) = pure dual-reference report.** Phase 1b-wire = pull arrays from `evaluate_labeled_batches` (`module_training_orchestration.py:462`, filtering `target_mu is None`) and emit the baseline artifact. Phases 2–4 per spec.

---

## File Structure

- **Create `src/calibration/baseline.py`** — `r_over_sigma_quantiles`, `TaskCalibration` dataclass, `evaluate_task_calibration`, and a private `_mean_crps_sampled` helper. One responsibility: turn one task's `(mu, sigma, target)` arrays into a dual-reference `TaskCalibration`. Imports numpy/scipy + Phase 0/1a modules only.
- **Modify `src/calibration/__init__.py`** — re-export `TaskCalibration`, `evaluate_task_calibration`, `r_over_sigma_quantiles`.
- **Create `tests/unit/calibration/test_baseline.py`** — synthetic-data TDD.

No other files change.

---

## Task 1: `r_over_sigma_quantiles` — the tail dashboard

**Files:**
- Create: `src/calibration/baseline.py`
- Test: `tests/unit/calibration/test_baseline.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/unit/calibration/test_baseline.py`:

```python
from __future__ import annotations

import numpy as np
import pytest

from src.calibration.baseline import r_over_sigma_quantiles


def test_r_over_sigma_zero_when_target_equals_mu() -> None:
    mu = np.zeros(100)
    sigma = np.ones(100)
    target = np.zeros(100)
    q = r_over_sigma_quantiles(mu, sigma, target)
    assert q["p50"] == pytest.approx(0.0)
    assert q["p95"] == pytest.approx(0.0)


def test_r_over_sigma_recovers_constant_standardized_residual() -> None:
    mu = np.zeros(1000)
    sigma = 2.0 * np.ones(1000)
    target = mu + 1.96 * sigma  # |r/sigma| == 1.96 everywhere
    q = r_over_sigma_quantiles(mu, sigma, target)
    assert q["p50"] == pytest.approx(1.96)
    assert q["p99"] == pytest.approx(1.96)


def test_r_over_sigma_default_keys() -> None:
    q = r_over_sigma_quantiles(np.zeros(10), np.ones(10), np.ones(10))
    assert set(q.keys()) == {"p50", "p90", "p95", "p99"}


def test_r_over_sigma_rejects_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="same shape"):
        r_over_sigma_quantiles(np.zeros(5), np.ones(5), np.ones(4))


def test_r_over_sigma_rejects_nonpositive_sigma() -> None:
    with pytest.raises(ValueError, match="sigma"):
        r_over_sigma_quantiles(np.zeros(3), np.array([1.0, 0.0, 1.0]), np.zeros(3))


def test_r_over_sigma_rejects_non_finite() -> None:
    with pytest.raises(ValueError, match="finite"):
        r_over_sigma_quantiles(np.zeros(3), np.ones(3), np.array([0.0, np.nan, 0.0]))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `py -m pytest tests/unit/calibration/test_baseline.py -v`
Expected: collection/import FAIL — `ModuleNotFoundError: No module named 'src.calibration.baseline'`.

- [ ] **Step 3: Implement the module with `r_over_sigma_quantiles`**

Create `src/calibration/baseline.py`:

```python
"""Per-task calibration baseline.

Scores a task's predictions under the current Gaussian assumption and a
Student-t reference on identical ``(mu, sigma, target)`` data, plus the
``|r/sigma|`` tail dashboard. Pure: operates on numpy arrays. The wiring that
pulls these arrays from the eval pipeline lives in Phase 1b-wire.

See docs/superpowers/specs/2026-05-31-student-t-migration-design.md.
"""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np


def _validate_triplet(
    mu: np.ndarray, sigma: np.ndarray, target: np.ndarray
) -> None:
    if not (mu.shape == sigma.shape == target.shape):
        raise ValueError("mu, sigma, target must have the same shape")
    if mu.ndim != 1 or mu.shape[0] == 0:
        raise ValueError("mu, sigma, target must be non-empty 1-D arrays")
    if not (
        np.all(np.isfinite(mu))
        and np.all(np.isfinite(sigma))
        and np.all(np.isfinite(target))
    ):
        raise ValueError("mu, sigma, target must all be finite (no NaN or inf)")
    if not np.all(sigma > 0.0):
        raise ValueError("sigma must be positive")


def r_over_sigma_quantiles(
    mu: np.ndarray,
    sigma: np.ndarray,
    target: np.ndarray,
    quantiles: Sequence[int] = (50, 90, 95, 99),
) -> Mapping[str, float]:
    """Quantiles of ``|r/sigma|`` (standardized residuals), ``r = target - mu``.

    The tail dashboard: a well-calibrated Gaussian has ``|r/sigma|`` p95 ~= 1.96;
    much larger means fat tails the Gaussian fails to capture.
    """
    mu = np.asarray(mu, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    target = np.asarray(target, dtype=float)
    _validate_triplet(mu, sigma, target)
    standardized = np.abs((target - mu) / sigma)
    return {f"p{int(q)}": float(np.percentile(standardized, q)) for q in quantiles}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `py -m pytest tests/unit/calibration/test_baseline.py -v`
Expected: PASS (6 tests).

- [ ] **Step 5: Commit**

```bash
git add src/calibration/baseline.py tests/unit/calibration/test_baseline.py
git commit -m "feat(calibration): add r/sigma tail-quantile dashboard"
```

---

## Task 2: `_mean_crps_sampled` — Student-t CRPS over samples

**Files:**
- Modify: `src/calibration/baseline.py`
- Test: `tests/unit/calibration/test_baseline.py`

- [ ] **Step 1: Add the failing tests**

Append to `tests/unit/calibration/test_baseline.py`:

```python
def test_mean_crps_sampled_matches_gaussian_closed_form() -> None:
    # PredictiveT with huge n_eff and high nu_loss ~= Normal(mu, sigma); its
    # sample-based mean CRPS should track the closed-form Gaussian CRPS.
    from src.calibration.baseline import _mean_crps_sampled
    from src.calibration.scoring import crps_gaussian
    from src.common.student_t import FormulaRule, predictive_t

    # nu_loss huge so the t is effectively Gaussian; n_eff huge so scale ~= sigma.
    dists = [
        predictive_t(mu=0.0, sigma=1.0, n_eff=1e6, nu_loss=1e6, rule=FormulaRule())
        for _ in range(2000)
    ]
    actuals = np.full(2000, 0.5)
    rng = np.random.default_rng(0)
    sampled = _mean_crps_sampled(dists, actuals, rng=rng, n_samples=2000)
    exact = crps_gaussian(mu=0.0, sigma=1.0, y=0.5)
    assert sampled == pytest.approx(exact, abs=0.02)


def test_mean_crps_sampled_is_positive() -> None:
    from src.calibration.baseline import _mean_crps_sampled
    from src.common.student_t import FormulaRule, predictive_t

    dists = [
        predictive_t(mu=0.0, sigma=1.0, n_eff=50.0, nu_loss=4.0, rule=FormulaRule())
        for _ in range(100)
    ]
    rng = np.random.default_rng(1)
    value = _mean_crps_sampled(dists, np.zeros(100), rng=rng, n_samples=500)
    assert value > 0.0
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `py -m pytest tests/unit/calibration/test_baseline.py -k mean_crps_sampled -v`
Expected: FAIL — `cannot import name '_mean_crps_sampled'`.

- [ ] **Step 3: Implement the helper**

Add these imports to the top of `src/calibration/baseline.py` (below the existing `import numpy as np`):

```python
from scipy import stats

from src.calibration.scoring import (
    CalibrationSummary,
    crps_from_samples,
    mean_crps_gaussian,
    summarize_calibration,
)
from src.common.student_t import PredictiveT, TailRule, predictive_t
```

Then append to `src/calibration/baseline.py`:

```python
def _mean_crps_sampled(
    dists: Sequence[PredictiveT],
    actuals: np.ndarray,
    *,
    rng: np.random.Generator,
    n_samples: int,
) -> float:
    """Mean sample-based CRPS over predictions that expose ``.sample``.

    Used for the Student-t reference, whose CRPS has no simple closed form here.
    Draws ``n_samples`` per prediction from the caller's RNG stream.
    """
    if len(dists) != actuals.shape[0]:
        raise ValueError("dists and actuals must have equal length")
    total = 0.0
    for dist, actual in zip(dists, actuals):
        samples = dist.sample(rng, size=n_samples)
        total += crps_from_samples(samples, float(actual))
    return total / len(dists)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `py -m pytest tests/unit/calibration/test_baseline.py -v`
Expected: PASS (Task 1 + Task 2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/calibration/baseline.py tests/unit/calibration/test_baseline.py
git commit -m "feat(calibration): add sample-based mean CRPS for Student-t reference"
```

---

## Task 3: `evaluate_task_calibration` — dual-reference rollup

**Files:**
- Modify: `src/calibration/baseline.py`
- Modify: `src/calibration/__init__.py`
- Test: `tests/unit/calibration/test_baseline.py`

- [ ] **Step 1: Add the failing tests**

Append to `tests/unit/calibration/test_baseline.py`:

```python
def _gaussian_task(n: int, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    mu = rng.normal(0.0, 1.0, size=n)
    sigma = np.full(n, 1.0)
    target = rng.normal(mu, sigma)  # actuals truly Gaussian around mu
    return mu, sigma, target


def test_evaluate_task_calibration_gaussian_world_is_well_calibrated() -> None:
    from src.calibration.baseline import evaluate_task_calibration
    from src.common.student_t import FormulaRule

    mu, sigma, target = _gaussian_task(8000, seed=3)
    result = evaluate_task_calibration(
        "driver_race",
        mu, sigma, target,
        nu_loss=4.0, rule=FormulaRule(), n_eff=1e6,
        levels=(0.9,), n_crps_samples=100, seed=5,
    )
    assert result.task == "driver_race"
    assert result.n == 8000
    # On truly-Gaussian data the Gaussian reference is calibrated...
    assert result.gaussian.coverage[0.9] == pytest.approx(0.90, abs=0.02)
    assert result.gaussian.pit_mean == pytest.approx(0.5, abs=0.02)
    # ...and the Student-t reference (t(4)) is fatter, so it OVER-covers here.
    assert result.student_t.coverage[0.9] > result.gaussian.coverage[0.9]
    # r/sigma p95 for calibrated Gaussian data is ~1.96.
    assert result.r_over_sigma["p95"] == pytest.approx(1.96, abs=0.15)


def test_evaluate_task_calibration_flags_heavy_tails() -> None:
    from src.calibration.baseline import evaluate_task_calibration
    from src.common.student_t import FormulaRule

    # Actuals heavier-tailed than Gaussian: target = mu + sigma * t(nu=3).
    rng = np.random.default_rng(9)
    n = 8000
    mu = np.zeros(n)
    sigma = np.ones(n)
    target = mu + sigma * rng.standard_t(df=3.0, size=n)
    result = evaluate_task_calibration(
        "quali",
        mu, sigma, target,
        nu_loss=4.0, rule=FormulaRule(), n_eff=1e6,
        levels=(0.95,), n_crps_samples=100, seed=2,
    )
    # The Gaussian world under-covers the fat-tailed truth at the 95% level;
    # the Student-t reference covers more (closer to nominal).
    assert result.gaussian.coverage[0.95] < 0.95
    assert result.student_t.coverage[0.95] > result.gaussian.coverage[0.95]
    # Fat tails show up in the dashboard: p99 of |r/sigma| well above the
    # Gaussian expectation (~2.58).
    assert result.r_over_sigma["p99"] > 3.0


def test_evaluate_task_calibration_reports_finite_crps_for_both() -> None:
    from src.calibration.baseline import evaluate_task_calibration
    from src.common.student_t import FormulaRule

    mu, sigma, target = _gaussian_task(2000, seed=7)
    result = evaluate_task_calibration(
        "race_start",
        mu, sigma, target,
        nu_loss=4.0, rule=FormulaRule(), n_eff=1e6,
        levels=(0.9,), n_crps_samples=100, seed=1,
    )
    assert np.isfinite(result.gaussian.crps) and result.gaussian.crps > 0.0
    assert np.isfinite(result.student_t.crps) and result.student_t.crps > 0.0
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `py -m pytest tests/unit/calibration/test_baseline.py -k evaluate_task -v`
Expected: FAIL — `cannot import name 'evaluate_task_calibration'`.

- [ ] **Step 3: Implement `TaskCalibration` and `evaluate_task_calibration`**

Append to `src/calibration/baseline.py`:

```python
@dataclass(frozen=True)
class TaskCalibration:
    """One task scored two ways on identical predictions, plus the tail dashboard."""

    task: str
    n: int
    gaussian: CalibrationSummary
    student_t: CalibrationSummary
    r_over_sigma: Mapping[str, float]


def evaluate_task_calibration(
    task: str,
    mu: np.ndarray,
    sigma: np.ndarray,
    target: np.ndarray,
    *,
    nu_loss: float,
    rule: TailRule,
    n_eff: float,
    levels: Sequence[float] = (0.5, 0.8, 0.9, 0.95),
    n_crps_samples: int = 200,
    seed: int = 0,
) -> TaskCalibration:
    """Score one task under the current Gaussian assumption and a Student-t
    reference on identical ``(mu, sigma, target)`` data.

    ``n_eff`` is applied uniformly here for the baseline (the per-site effective
    sample size is wired in later phases); pass a large value to preview the pure
    aleatoric ``t(nu_loss)`` with negligible epistemic inflation.
    """
    mu = np.asarray(mu, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    target = np.asarray(target, dtype=float)
    _validate_triplet(mu, sigma, target)

    gaussian_dists = [
        stats.norm(loc=float(m), scale=float(s)) for m, s in zip(mu, sigma)
    ]
    student_dists = [
        predictive_t(mu=float(m), sigma=float(s), n_eff=n_eff, nu_loss=nu_loss, rule=rule)
        for m, s in zip(mu, sigma)
    ]

    gaussian_crps = mean_crps_gaussian(mu, sigma, target)
    rng = np.random.default_rng(seed)
    student_crps = _mean_crps_sampled(
        student_dists, target, rng=rng, n_samples=n_crps_samples
    )

    gaussian = summarize_calibration(
        dists=gaussian_dists, actuals=target, crps=gaussian_crps, levels=levels
    )
    student = summarize_calibration(
        dists=student_dists, actuals=target, crps=student_crps, levels=levels
    )
    return TaskCalibration(
        task=task,
        n=int(target.shape[0]),
        gaussian=gaussian,
        student_t=student,
        r_over_sigma=r_over_sigma_quantiles(mu, sigma, target),
    )
```

Add `from dataclasses import dataclass` to the top-level imports of `src/calibration/baseline.py` (the import section should begin):

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
from scipy import stats
```

- [ ] **Step 4: Export the new public names**

In `src/calibration/__init__.py`, add a second import block and extend `__all__`:

```python
from src.calibration.baseline import (
    TaskCalibration,
    evaluate_task_calibration,
    r_over_sigma_quantiles,
)
```

Add `"TaskCalibration"`, `"evaluate_task_calibration"`, `"r_over_sigma_quantiles"` to the `__all__` list.

- [ ] **Step 5: Run the full calibration suite to verify it passes**

Run: `py -m pytest tests/unit/calibration/ -v`
Expected: PASS (all scoring + baseline tests).

- [ ] **Step 6: Commit**

```bash
git add src/calibration/baseline.py src/calibration/__init__.py tests/unit/calibration/test_baseline.py
git commit -m "feat(calibration): add dual-reference per-task calibration evaluation"
```

---

## Task 4: Import surface + regression

**Files:**
- Test/verify only.

- [ ] **Step 1: Confirm the public API imports cleanly**

Run: `py -c "from src.calibration import evaluate_task_calibration, TaskCalibration, r_over_sigma_quantiles; print('ok')"`
Expected: prints `ok`.

- [ ] **Step 2: Run the full calibration package suite**

Run: `py -m pytest tests/unit/calibration/ -v`
Expected: PASS (scoring + baseline).

- [ ] **Step 3: Confirm no regression in the dependency modules**

Run: `py -m pytest tests/unit/calibration tests/unit/common -q`
Expected: PASS.

- [ ] **Step 4: Commit (only if any file changed in this task; otherwise skip)**

If `git status` shows changes:

```bash
git add -A
git commit -m "chore(calibration): verify Phase 1b-core import surface and regression"
```

If nothing changed, this task is verification-only — note that and finish.

---

## Self-Review Notes (for the implementer)

- **Spec coverage:** Implements the Phase 1 "measure first" comparison — current-Gaussian vs Student-t coverage gate + CRPS score + `r/sigma` dashboard — as a pure, testable per-task function. The DB/CLI wiring that supplies real `(mu, sigma, target)` arrays (filtering `target_mu is None`) is Phase 1b-wire, out of scope here.
- **Modeling choices made explicit (revisitable in 1b-wire/Phase 4):** `n_eff` is applied uniformly (caller passes a large value for the pure-aleatoric baseline); Student-t CRPS is sample-based (`n_crps_samples`, seeded) while Gaussian CRPS is the exact closed form.
- **Type consistency:** `r_over_sigma_quantiles(mu, sigma, target, quantiles)`, `_mean_crps_sampled(dists, actuals, *, rng, n_samples)`, `evaluate_task_calibration(task, mu, sigma, target, *, nu_loss, rule, n_eff, levels, n_crps_samples, seed)` — names/signatures stable across tasks and the `__init__` exports. `TaskCalibration(task, n, gaussian, student_t, r_over_sigma)`.
- **Pyright:** explicit return types, `from __future__ import annotations`, no `Any`, no `# type: ignore`.

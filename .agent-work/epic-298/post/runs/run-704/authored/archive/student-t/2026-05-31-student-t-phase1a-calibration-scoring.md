# Student-t Phase 1a: Calibration Scoring Core — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the pure, distribution-agnostic scoring core of the calibration harness — PIT values, interval coverage, and CRPS — that judges whether a predictive distribution matches realized outcomes. No DB, no model, no behavior change to existing code.

**Architecture:** A new top-level package `src/calibration/` with one pure module `scoring.py`. Functions operate on plain numpy arrays plus duck-typed "frozen distribution" objects (anything exposing `.cdf(x)` and `.interval(level)` — both `scipy.stats` frozen dists and our `src/common/student_t.PredictiveT` qualify). This lets the same code score the current Gaussian baseline and the future Student-t predictions identically. CRPS is provided in a closed form for the Gaussian baseline and a general sample-based estimator for arbitrary distributions; the two are cross-validated against each other in tests.

**Tech Stack:** Python 3.11, numpy, scipy.stats (both declared in `pyproject.toml`), pytest. Python is invoked as `py`; tests run via `py -m pytest`. Pyright runs in CI in `basic` mode — every function needs explicit return types and `from __future__ import annotations`.

**Spec:** `docs/superpowers/specs/2026-05-31-student-t-migration-design.md` (Acceptance signal: coverage/PIT is the gate, CRPS the proper score; `r/sigma` p95/p99 the dashboard — the dashboard lives in Phase 1b).

**Roadmap context (each its own plan):** Phase 0 (done) = `src/common/student_t.py` foundation. **Phase 1a (this) = scoring core.** Phase 1b = backtest harness wiring scoring to `evaluate_labeled_batches` + extend the `r/sigma` dashboard, emit a baseline report. Phases 2–4 as in the spec.

---

## File Structure

- **Create `src/calibration/__init__.py`** — package marker; re-exports the public scoring API.
- **Create `src/calibration/scoring.py`** — all scoring functions and the `CalibrationSummary` dataclass. One responsibility: turn `(predictive dists | samples, actuals)` into calibration numbers. Pure; imports only numpy/scipy/stdlib.
- **Create `tests/unit/calibration/__init__.py`** — empty package marker (required; mirrors other `tests/unit/*/__init__.py`).
- **Create `tests/unit/calibration/test_scoring.py`** — known-answer + property tests.

No existing files are modified in Phase 1a.

---

## Task 1: PIT values and interval coverage

**Files:**
- Create: `src/calibration/__init__.py`
- Create: `src/calibration/scoring.py`
- Create: `tests/unit/calibration/__init__.py`
- Create: `tests/unit/calibration/test_scoring.py`

- [ ] **Step 1: Create the package markers**

Create `src/calibration/__init__.py` with:

```python
"""Calibration scoring and (later) backtest harness for predictive distributions."""

from src.calibration.scoring import (
    coverage_curve,
    interval_coverage,
    pit_values,
)

__all__ = [
    "pit_values",
    "interval_coverage",
    "coverage_curve",
]
```

Create `tests/unit/calibration/__init__.py` as an empty file:

```python
```

- [ ] **Step 2: Write the failing tests**

Create `tests/unit/calibration/test_scoring.py`:

```python
from __future__ import annotations

import numpy as np
import pytest
from scipy import stats

from src.calibration.scoring import coverage_curve, interval_coverage, pit_values


def test_pit_values_equal_cdf_at_actuals() -> None:
    dists = [stats.norm(loc=0.0, scale=1.0), stats.norm(loc=5.0, scale=2.0)]
    actuals = np.array([0.0, 5.0])
    pit = pit_values(dists, actuals)
    # At the median of each distribution the CDF is exactly 0.5.
    np.testing.assert_allclose(pit, [0.5, 0.5])


def test_pit_values_are_uniform_when_actuals_drawn_from_predictive() -> None:
    rng = np.random.default_rng(0)
    n = 20000
    dist = stats.norm(loc=0.0, scale=1.0)
    actuals = dist.rvs(size=n, random_state=rng)
    pit = pit_values([dist] * n, actuals)
    assert pit.shape == (n,)
    assert pit.min() >= 0.0 and pit.max() <= 1.0
    # A well-calibrated PIT is Uniform(0,1): mean ~0.5, variance ~1/12.
    assert float(np.mean(pit)) == pytest.approx(0.5, abs=0.02)
    assert float(np.var(pit)) == pytest.approx(1.0 / 12.0, abs=0.01)


def test_pit_values_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError, match="length"):
        pit_values([stats.norm()], np.array([0.0, 1.0]))


def test_interval_coverage_matches_nominal_when_calibrated() -> None:
    rng = np.random.default_rng(1)
    n = 20000
    dist = stats.norm(loc=0.0, scale=1.0)
    actuals = dist.rvs(size=n, random_state=rng)
    cov = interval_coverage([dist] * n, actuals, level=0.90)
    assert cov == pytest.approx(0.90, abs=0.02)


def test_interval_coverage_is_low_for_overconfident_predictions() -> None:
    # Predict a too-narrow distribution; actuals spread wider -> under-coverage.
    rng = np.random.default_rng(2)
    n = 20000
    actuals = stats.norm(loc=0.0, scale=3.0).rvs(size=n, random_state=rng)
    overconfident = stats.norm(loc=0.0, scale=1.0)
    cov = interval_coverage([overconfident] * n, actuals, level=0.90)
    assert cov < 0.75


def test_coverage_curve_returns_coverage_per_level() -> None:
    rng = np.random.default_rng(3)
    n = 20000
    dist = stats.norm(loc=0.0, scale=1.0)
    actuals = dist.rvs(size=n, random_state=rng)
    curve = coverage_curve([dist] * n, actuals, levels=(0.5, 0.8, 0.95))
    assert set(curve.keys()) == {0.5, 0.8, 0.95}
    for level, cov in curve.items():
        assert cov == pytest.approx(level, abs=0.02)
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `py -m pytest tests/unit/calibration/test_scoring.py -v`
Expected: collection/import FAIL — `ModuleNotFoundError: No module named 'src.calibration.scoring'`.

- [ ] **Step 4: Implement PIT and coverage**

Create `src/calibration/scoring.py`:

```python
"""Pure scoring functions for predictive-distribution calibration.

Distribution-agnostic: any object exposing ``.cdf(x)`` and ``.interval(level)``
works — both ``scipy.stats`` frozen distributions and
``src.common.student_t.PredictiveT``. No DB, model, or I/O here.

See docs/superpowers/specs/2026-05-31-student-t-migration-design.md.
"""

from __future__ import annotations

from typing import Mapping, Protocol, Sequence

import numpy as np


class PredictiveDist(Protocol):
    """Minimal frozen-distribution interface used by the calibration scorers."""

    def cdf(self, x: float) -> float:
        ...

    def interval(self, level: float) -> tuple[float, float]:
        ...


def _check_lengths(dists: Sequence[PredictiveDist], actuals: np.ndarray) -> None:
    if len(dists) != actuals.shape[0]:
        raise ValueError(
            f"dists and actuals must have equal length, got {len(dists)} and "
            f"{actuals.shape[0]}"
        )


def pit_values(
    dists: Sequence[PredictiveDist], actuals: np.ndarray
) -> np.ndarray:
    """Probability Integral Transform: ``F_i(actual_i)`` for each prediction.

    Under perfect calibration these are Uniform(0, 1). Deviations reveal bias
    (mean off 0.5) or wrong spread (variance off 1/12).
    """
    actuals = np.asarray(actuals, dtype=float)
    _check_lengths(dists, actuals)
    return np.array(
        [float(dist.cdf(float(actual))) for dist, actual in zip(dists, actuals)],
        dtype=float,
    )


def interval_coverage(
    dists: Sequence[PredictiveDist], actuals: np.ndarray, level: float
) -> float:
    """Empirical coverage of the central ``level`` interval.

    Returns the fraction of actuals that fall inside each prediction's central
    interval. A calibrated model returns ~``level``.
    """
    actuals = np.asarray(actuals, dtype=float)
    _check_lengths(dists, actuals)
    if not (0.0 < level < 1.0):
        raise ValueError(f"level must be in (0, 1), got {level}")
    inside = 0
    for dist, actual in zip(dists, actuals):
        lo, hi = dist.interval(level)
        if lo <= float(actual) <= hi:
            inside += 1
    return inside / len(dists)


def coverage_curve(
    dists: Sequence[PredictiveDist],
    actuals: np.ndarray,
    levels: Sequence[float],
) -> Mapping[float, float]:
    """Empirical coverage at several nominal levels (a reliability curve)."""
    return {float(level): interval_coverage(dists, actuals, level) for level in levels}
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `py -m pytest tests/unit/calibration/test_scoring.py -v`
Expected: PASS (6 tests).

- [ ] **Step 6: Commit**

```bash
git add src/calibration/__init__.py src/calibration/scoring.py tests/unit/calibration/__init__.py tests/unit/calibration/test_scoring.py
git commit -m "feat(calibration): add PIT values and interval coverage scorers"
```

---

## Task 2: CRPS — closed-form Gaussian and general sample-based

**Files:**
- Modify: `src/calibration/scoring.py`
- Modify: `src/calibration/__init__.py`
- Test: `tests/unit/calibration/test_scoring.py`

- [ ] **Step 1: Add the failing CRPS tests**

Append to `tests/unit/calibration/test_scoring.py`:

```python
def test_crps_gaussian_known_value_at_mean() -> None:
    # Closed form at y = mu, sigma = 1: CRPS = sqrt(2/pi) - 1/sqrt(pi) ~= 0.2337.
    from src.calibration.scoring import crps_gaussian

    value = crps_gaussian(mu=0.0, sigma=1.0, y=0.0)
    assert value == pytest.approx(np.sqrt(2.0 / np.pi) - 1.0 / np.sqrt(np.pi))
    assert value == pytest.approx(0.23370, abs=1e-4)


def test_crps_gaussian_scales_linearly_with_sigma() -> None:
    from src.calibration.scoring import crps_gaussian

    base = crps_gaussian(mu=0.0, sigma=1.0, y=0.0)
    assert crps_gaussian(mu=0.0, sigma=2.0, y=0.0) == pytest.approx(2.0 * base)


def test_crps_gaussian_is_lower_for_a_better_prediction() -> None:
    from src.calibration.scoring import crps_gaussian

    # A prediction centred on the outcome beats one that is off.
    on_target = crps_gaussian(mu=0.0, sigma=1.0, y=0.0)
    off_target = crps_gaussian(mu=3.0, sigma=1.0, y=0.0)
    assert on_target < off_target


def test_crps_from_samples_hand_computed() -> None:
    from src.calibration.scoring import crps_from_samples

    # samples [0, 2], y = 1: mean|s-y| = 1; E|X-X'| over all ordered pairs = 1;
    # CRPS = 1 - 0.5*1 = 0.5.
    value = crps_from_samples(np.array([0.0, 2.0]), actual=1.0)
    assert value == pytest.approx(0.5)


def test_crps_from_samples_approximates_gaussian_closed_form() -> None:
    from src.calibration.scoring import crps_from_samples, crps_gaussian

    rng = np.random.default_rng(7)
    samples = rng.normal(loc=0.0, scale=1.0, size=50000)
    approx = crps_from_samples(samples, actual=0.5)
    exact = crps_gaussian(mu=0.0, sigma=1.0, y=0.5)
    assert approx == pytest.approx(exact, abs=0.01)


def test_mean_crps_gaussian_averages_over_predictions() -> None:
    from src.calibration.scoring import crps_gaussian, mean_crps_gaussian

    mus = np.array([0.0, 1.0])
    sigmas = np.array([1.0, 1.0])
    ys = np.array([0.0, 1.0])
    expected = 0.5 * (
        crps_gaussian(mu=0.0, sigma=1.0, y=0.0)
        + crps_gaussian(mu=1.0, sigma=1.0, y=1.0)
    )
    assert mean_crps_gaussian(mus, sigmas, ys) == pytest.approx(expected)
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `py -m pytest tests/unit/calibration/test_scoring.py -k crps -v`
Expected: FAIL — `ImportError`/`cannot import name 'crps_gaussian'` (and the other CRPS names).

- [ ] **Step 3: Implement CRPS**

First, add scipy to the top-level imports of `src/calibration/scoring.py`. Change the import section so it reads (add the `from scipy import stats` line next to the numpy import):

```python
import numpy as np
from scipy import stats
```

Then append the CRPS functions to the END of `src/calibration/scoring.py`:

```python
def crps_gaussian(mu: float, sigma: float, y: float) -> float:
    """Closed-form CRPS of a Gaussian prediction against scalar outcome ``y``.

    CRPS(N(mu, sigma), y) = sigma * [ w*(2*Phi(w) - 1) + 2*phi(w) - 1/sqrt(pi) ],
    where w = (y - mu) / sigma. Lower is better. Used for the Gaussian baseline
    and to validate the sample-based estimator.
    """
    if not (sigma > 0.0):
        raise ValueError(f"sigma must be positive, got {sigma}")
    w = (y - mu) / sigma
    phi = float(stats.norm.pdf(w))
    cdf = float(stats.norm.cdf(w))
    return float(sigma * (w * (2.0 * cdf - 1.0) + 2.0 * phi - 1.0 / np.sqrt(np.pi)))


def mean_crps_gaussian(
    mus: np.ndarray, sigmas: np.ndarray, ys: np.ndarray
) -> float:
    """Mean Gaussian CRPS over arrays of predictions/outcomes."""
    mus = np.asarray(mus, dtype=float)
    sigmas = np.asarray(sigmas, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if not (mus.shape == sigmas.shape == ys.shape):
        raise ValueError("mus, sigmas, ys must have the same shape")
    return float(
        np.mean(
            [crps_gaussian(float(m), float(s), float(y)) for m, s, y in zip(mus, sigmas, ys)]
        )
    )


def crps_from_samples(samples: np.ndarray, actual: float) -> float:
    """Sample-based CRPS estimator for an arbitrary predictive distribution.

    CRPS = E|X - y| - 0.5 * E|X - X'|, where X, X' are independent draws. The
    second expectation uses the sorted-sample identity
    E|X - X'| = (2 / S^2) * sum_i (2i - S - 1) * x_(i)  (1-indexed, x sorted),
    which is O(S log S). Works for any distribution that can be sampled,
    including ``src.common.student_t.PredictiveT.sample``.
    """
    samples = np.asarray(samples, dtype=float)
    if samples.ndim != 1 or samples.shape[0] == 0:
        raise ValueError("samples must be a non-empty 1-D array")
    s = samples.shape[0]
    term_abs = float(np.mean(np.abs(samples - actual)))
    sorted_samples = np.sort(samples)
    i = np.arange(1, s + 1, dtype=float)
    e_xx = float((2.0 / (s * s)) * np.sum((2.0 * i - s - 1.0) * sorted_samples))
    return term_abs - 0.5 * e_xx
```

- [ ] **Step 4: Export the new functions**

In `src/calibration/__init__.py`, update the import block and `__all__` to include the CRPS functions:

```python
"""Calibration scoring and (later) backtest harness for predictive distributions."""

from src.calibration.scoring import (
    coverage_curve,
    crps_from_samples,
    crps_gaussian,
    interval_coverage,
    mean_crps_gaussian,
    pit_values,
)

__all__ = [
    "pit_values",
    "interval_coverage",
    "coverage_curve",
    "crps_gaussian",
    "mean_crps_gaussian",
    "crps_from_samples",
]
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `py -m pytest tests/unit/calibration/test_scoring.py -v`
Expected: PASS (all Task 1 + Task 2 tests).

- [ ] **Step 6: Commit**

```bash
git add src/calibration/scoring.py src/calibration/__init__.py tests/unit/calibration/test_scoring.py
git commit -m "feat(calibration): add Gaussian and sample-based CRPS scorers"
```

---

## Task 3: `CalibrationSummary` — one-call per-task rollup

**Files:**
- Modify: `src/calibration/scoring.py`
- Modify: `src/calibration/__init__.py`
- Test: `tests/unit/calibration/test_scoring.py`

- [ ] **Step 1: Add the failing tests**

Append to `tests/unit/calibration/test_scoring.py`:

```python
def test_summarize_calibration_reports_gate_and_score() -> None:
    from src.calibration.scoring import summarize_calibration

    rng = np.random.default_rng(11)
    n = 20000
    dist = stats.norm(loc=0.0, scale=1.0)
    actuals = dist.rvs(size=n, random_state=rng)
    summary = summarize_calibration(
        dists=[dist] * n,
        actuals=actuals,
        crps=float(np.mean([0.2 for _ in range(n)])),  # placeholder scalar CRPS
        levels=(0.5, 0.9),
    )
    assert summary.n == n
    assert summary.coverage[0.5] == pytest.approx(0.5, abs=0.02)
    assert summary.coverage[0.9] == pytest.approx(0.9, abs=0.02)
    assert summary.pit_mean == pytest.approx(0.5, abs=0.02)
    assert summary.crps == pytest.approx(0.2)


def test_summarize_calibration_flags_miscalibration() -> None:
    from src.calibration.scoring import summarize_calibration

    rng = np.random.default_rng(12)
    n = 20000
    actuals = stats.norm(loc=0.0, scale=3.0).rvs(size=n, random_state=rng)
    overconfident = stats.norm(loc=0.0, scale=1.0)
    summary = summarize_calibration(
        dists=[overconfident] * n, actuals=actuals, crps=1.0, levels=(0.9,)
    )
    # Over-confident model under-covers at the 90% level.
    assert summary.coverage[0.9] < 0.75
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `py -m pytest tests/unit/calibration/test_scoring.py -k summarize -v`
Expected: FAIL — `cannot import name 'summarize_calibration'`.

- [ ] **Step 3: Implement the summary**

First, add the dataclass import to the top-level imports of `src/calibration/scoring.py`. The top import section should read:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence

import numpy as np
from scipy import stats
```

Then append the summary to the END of `src/calibration/scoring.py`:

```python
@dataclass(frozen=True)
class CalibrationSummary:
    """Per-task calibration rollup: coverage gate, PIT diagnostics, CRPS score."""

    n: int
    coverage: Mapping[float, float]
    pit_mean: float
    pit_var: float
    crps: float


def summarize_calibration(
    *,
    dists: Sequence[PredictiveDist],
    actuals: np.ndarray,
    crps: float,
    levels: Sequence[float] = (0.5, 0.8, 0.9, 0.95),
) -> CalibrationSummary:
    """Roll up the calibration gate (coverage), PIT diagnostics, and CRPS.

    ``crps`` is passed in (computed by the caller via ``mean_crps_gaussian`` or
    ``crps_from_samples``) so this function stays distribution-agnostic and does
    not assume how the predictive was sampled.
    """
    actuals = np.asarray(actuals, dtype=float)
    pit = pit_values(dists, actuals)
    return CalibrationSummary(
        n=int(actuals.shape[0]),
        coverage=coverage_curve(dists, actuals, levels),
        pit_mean=float(np.mean(pit)),
        pit_var=float(np.var(pit)),
        crps=float(crps),
    )
```

- [ ] **Step 4: Export `CalibrationSummary` and `summarize_calibration`**

Update `src/calibration/__init__.py` import block and `__all__` to add `CalibrationSummary` and `summarize_calibration`:

```python
"""Calibration scoring and (later) backtest harness for predictive distributions."""

from src.calibration.scoring import (
    CalibrationSummary,
    coverage_curve,
    crps_from_samples,
    crps_gaussian,
    interval_coverage,
    mean_crps_gaussian,
    pit_values,
    summarize_calibration,
)

__all__ = [
    "pit_values",
    "interval_coverage",
    "coverage_curve",
    "crps_gaussian",
    "mean_crps_gaussian",
    "crps_from_samples",
    "CalibrationSummary",
    "summarize_calibration",
]
```

- [ ] **Step 5: Run the full module test suite to verify it passes**

Run: `py -m pytest tests/unit/calibration/ -v`
Expected: PASS (all tasks' tests).

- [ ] **Step 6: Commit**

```bash
git add src/calibration/scoring.py src/calibration/__init__.py tests/unit/calibration/test_scoring.py
git commit -m "feat(calibration): add CalibrationSummary per-task rollup"
```

---

## Task 4: Cross-distribution check + regression

**Files:**
- Test: `tests/unit/calibration/test_scoring.py`

- [ ] **Step 1: Add a test that the scorers work on `PredictiveT` (not just scipy dists)**

This proves the duck-typed `PredictiveDist` protocol genuinely covers our Phase 0 distribution, which is what Phase 2+ will feed in. Append to `tests/unit/calibration/test_scoring.py`:

```python
def test_scorers_accept_predictive_t_instances() -> None:
    from src.calibration.scoring import (
        coverage_curve,
        crps_from_samples,
        pit_values,
    )
    from src.common.student_t import FormulaRule, predictive_t

    rng = np.random.default_rng(21)
    n = 4000
    dists = [
        predictive_t(mu=0.0, sigma=1.0, n_eff=50.0, nu_loss=4.0, rule=FormulaRule())
        for _ in range(n)
    ]
    # Draw actuals from the same predictive so calibration should look good.
    actuals = np.array([d.sample(rng, size=()) for d in dists], dtype=float)

    pit = pit_values(dists, actuals)
    assert pit.min() >= 0.0 and pit.max() <= 1.0
    assert float(np.mean(pit)) == pytest.approx(0.5, abs=0.03)

    curve = coverage_curve(dists, actuals, levels=(0.9,))
    assert curve[0.9] == pytest.approx(0.9, abs=0.03)

    # Sample-based CRPS works on PredictiveT samples for a single prediction.
    samples = dists[0].sample(rng, size=20000)
    value = crps_from_samples(samples, actual=0.0)
    assert value > 0.0
```

- [ ] **Step 2: Run the test to verify it passes**

Run: `py -m pytest tests/unit/calibration/test_scoring.py::test_scorers_accept_predictive_t_instances -v`
Expected: PASS (no production code change needed — this verifies the protocol already covers `PredictiveT`). If it fails because `PredictiveT` lacks `.cdf`/`.interval`, STOP and report — do not modify production code without escalating.

- [ ] **Step 3: Run the full calibration suite and confirm no regressions elsewhere**

Run: `py -m pytest tests/unit/calibration/ -v`
Expected: PASS (all tests).

Then confirm the module imports cleanly:

Run: `py -c "from src.calibration import summarize_calibration, crps_gaussian, pit_values; print('ok')"`
Expected: prints `ok`.

- [ ] **Step 4: Commit**

```bash
git add tests/unit/calibration/test_scoring.py
git commit -m "test(calibration): verify scorers accept PredictiveT via the protocol"
```

---

## Self-Review Notes (for the implementer)

- **Spec coverage:** Implements the Phase 1 "gate" (interval coverage + PIT) and "proper score" (CRPS) as pure, testable functions. The `r/sigma` p95/p99 dashboard and the live backtest wiring are Phase 1b, deliberately out of scope here.
- **Distribution-agnostic by design:** scorers depend only on the `PredictiveDist` protocol (`.cdf`, `.interval`) plus sample arrays, so they score the current Gaussian baseline (`scipy.stats.norm`) and the future `PredictiveT` identically. Task 4 pins that.
- **CRPS validation:** the closed-form Gaussian and the sample-based estimator are cross-checked against each other (Task 2), and the sample estimator has a hand-computed known answer.
- **Type consistency:** `pit_values(dists, actuals)`, `interval_coverage(dists, actuals, level)`, `coverage_curve(dists, actuals, levels)`, `crps_gaussian(mu, sigma, y)`, `mean_crps_gaussian(mus, sigmas, ys)`, `crps_from_samples(samples, actual)`, `summarize_calibration(*, dists, actuals, crps, levels)` — names and signatures are stable across tasks and exports.
- **Pyright:** every function has explicit return types and `from __future__ import annotations`; no `Any`, no `# type: ignore`.

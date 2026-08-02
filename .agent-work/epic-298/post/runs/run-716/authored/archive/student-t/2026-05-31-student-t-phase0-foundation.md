# Student-t Phase 0: Foundation Module — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the shared `predictive_t` seam — a sample-size-adaptive Student-t predictive distribution that every sampler/interval call site will route through — with no behavior change to existing code.

**Architecture:** A single new module `src/common/student_t.py` exposes (1) a `PredictiveT` frozen distribution wrapping `scipy.stats.t` with location/scale, (2) two pluggable tail rules (`FormulaRule`, `HybridRule`) mapping effective sample size to a predictive `nu`, and (3) a `predictive_t()` factory that composes the fixed aleatoric loss `nu` with epistemic widening (fatter tails + inflated scale) under the invariant *epistemic only fattens, clamping at `nu_loss`*. Nothing calls it yet, so nothing can regress.

**Tech Stack:** Python 3, numpy, scipy.stats (both already declared in `pyproject.toml`), pytest. Python is invoked as `py`; tests run via `py -m pytest`.

**Spec:** `docs/superpowers/specs/2026-05-31-student-t-migration-design.md`

**Roadmap (each its own future plan, written once this API is concrete):**
- **Phase 1** — `src/calibration/` harness: PIT coverage + CRPS scoring, baseline the current Gaussian world.
- **Phase 2** — Route the fantasy sampler (`src/fantasy_scoring/expected_assignment.py`) through `predictive_t`.
- **Phase 3** — Remaining Gaussian interval sites: quali `norm.cdf`, tire-wear CIs (per-compound `n_eff`), viz bands.
- **Phase 4** — Tune `FormulaRule` vs `HybridRule` + `tau` per task against the harness; lock in.

---

## File Structure

- **Create `src/common/student_t.py`** — the entire foundation: `PredictiveT`, `TailRule`, `FormulaRule`, `HybridRule`, `predictive_t()`, `NU_FLOOR`. One responsibility: turn `(mu, sigma, n_eff)` + a rule into a frozen predictive distribution. Lives in `src/common/` next to the existing `distribution_utils.py`.
- **Create `tests/unit/common/__init__.py`** — empty package marker (mirrors `tests/unit/latent_power/__init__.py`).
- **Create `tests/unit/common/test_student_t.py`** — unit tests for the rules, the factory, the invariant, and the distribution methods.

No existing files are modified in Phase 0.

---

## Task 1: Tail rules (`FormulaRule`, `HybridRule`)

**Files:**
- Create: `src/common/student_t.py`
- Create: `tests/unit/common/__init__.py`
- Create: `tests/unit/common/test_student_t.py`

- [ ] **Step 1: Create the test package marker**

Create `tests/unit/common/__init__.py` as an empty file:

```python
```

(Empty file — mirrors the other `tests/unit/*/__init__.py` markers so pytest collects the package.)

- [ ] **Step 2: Write the failing tests for the tail rules**

Create `tests/unit/common/test_student_t.py`:

```python
from __future__ import annotations

import math

import numpy as np
import pytest

from src.common.student_t import FormulaRule, HybridRule


def test_formula_rule_clamps_at_nu_loss() -> None:
    # Abundant effective data -> ride the aleatoric floor, never thinner.
    rule = FormulaRule(nu_prior=2.5, k=1.0)
    assert rule.nu(nu_loss=4.0, n_eff=100.0) == 4.0


def test_formula_rule_fattens_for_small_n() -> None:
    rule = FormulaRule(nu_prior=2.5, k=1.0)
    # nu = min(20, 2.5 + 1.0 * 0.5) = 3.0
    assert rule.nu(nu_loss=20.0, n_eff=0.5) == pytest.approx(3.0)


def test_formula_rule_approaches_nu_prior_at_tiny_n() -> None:
    rule = FormulaRule(nu_prior=2.5, k=1.0)
    assert rule.nu(nu_loss=20.0, n_eff=1e-9) == pytest.approx(2.5, abs=1e-6)


def test_hybrid_rule_without_fit_equals_formula() -> None:
    hybrid = HybridRule(nu_prior=2.5, k=1.0, tau=10.0)
    formula = FormulaRule(nu_prior=2.5, k=1.0)
    assert hybrid.nu(nu_loss=20.0, n_eff=3.0, nu_fit=None) == pytest.approx(
        formula.nu(nu_loss=20.0, n_eff=3.0)
    )


def test_hybrid_rule_shrinks_toward_fit_with_data() -> None:
    # tau=10, n_eff=10 -> w = 10/20 = 0.5.
    # formula = 2.5 + 10 = 12.5 ; blended = 0.5*8 + 0.5*12.5 = 10.25 ; below nu_loss=20.
    hybrid = HybridRule(nu_prior=2.5, k=1.0, tau=10.0)
    assert hybrid.nu(nu_loss=20.0, n_eff=10.0, nu_fit=8.0) == pytest.approx(10.25)


def test_hybrid_rule_still_clamps_at_nu_loss() -> None:
    hybrid = HybridRule(nu_prior=2.5, k=1.0, tau=10.0)
    # A large fit + large n must not exceed the aleatoric floor.
    assert hybrid.nu(nu_loss=4.0, n_eff=50.0, nu_fit=30.0) == 4.0
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `py -m pytest tests/unit/common/test_student_t.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.common.student_t'`

- [ ] **Step 4: Write the module with the rules**

Create `src/common/student_t.py`:

```python
"""Sample-adaptive Student-t predictive distributions.

The single seam between trained models (mu, sigma) and every consumer that
samples or builds intervals. Composes the fixed *aleatoric* loss nu with an
*epistemic*, sample-size-driven widening.

See docs/superpowers/specs/2026-05-31-student-t-migration-design.md.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

import numpy as np
from scipy import stats

# Student-t variance is finite only for nu > 2; the latent-power loss already
# hard-floors at 2. Keep a small margin so variance-based code stays well-defined.
NU_FLOOR: float = 2.0 + 1e-6


class TailRule(Protocol):
    """Maps (aleatoric nu_loss, effective sample size) to a predictive nu."""

    def nu(self, *, nu_loss: float, n_eff: float, nu_fit: float | None = None) -> float:
        ...


@dataclass(frozen=True)
class FormulaRule:
    """Closed-form epistemic df: nu = nu_prior + k * n_eff, clamped at nu_loss.

    Recovers the classical result that estimating scale from n effective
    observations yields a predictive t with df ~ n. nu_prior is the fattest tail
    the rule will ever produce (at n_eff -> 0).
    """

    nu_prior: float = 2.5
    k: float = 1.0

    def nu(self, *, nu_loss: float, n_eff: float, nu_fit: float | None = None) -> float:
        epistemic = self.nu_prior + self.k * n_eff
        return float(min(nu_loss, epistemic))


@dataclass(frozen=True)
class HybridRule:
    """MLE nu_fit shrunk toward the formula prior.

    Weight w = n_eff / (n_eff + tau): data-rich tasks trust the fitted tail,
    data-starved tasks fall back to the principled formula. Always clamped at
    nu_loss so epistemic uncertainty can only fatten, never thin.
    """

    nu_prior: float = 2.5
    k: float = 1.0
    tau: float = 10.0

    def nu(self, *, nu_loss: float, n_eff: float, nu_fit: float | None = None) -> float:
        formula = self.nu_prior + self.k * n_eff
        if nu_fit is None:
            blended = formula
        else:
            w = n_eff / (n_eff + self.tau)
            blended = w * float(nu_fit) + (1.0 - w) * formula
        return float(min(nu_loss, blended))
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `py -m pytest tests/unit/common/test_student_t.py -v`
Expected: PASS (6 passed)

- [ ] **Step 6: Commit**

```bash
git add src/common/student_t.py tests/unit/common/__init__.py tests/unit/common/test_student_t.py
git commit -m "feat(student-t): add sample-adaptive tail rules (formula + hybrid)"
```

---

## Task 2: `PredictiveT` distribution wrapper

**Files:**
- Modify: `src/common/student_t.py`
- Test: `tests/unit/common/test_student_t.py`

- [ ] **Step 1: Add the failing tests for `PredictiveT`**

First, update the import block at the top of `tests/unit/common/test_student_t.py` to bring in the new names this task uses (`NU_FLOOR`, `PredictiveT`, and `scipy.stats`):

```python
from src.common.student_t import FormulaRule, HybridRule, NU_FLOOR, PredictiveT
from scipy import stats
```

Then append these tests:

```python
def test_predictive_t_rejects_nu_at_or_below_floor() -> None:
    with pytest.raises(ValueError, match="finite variance"):
        PredictiveT(nu=NU_FLOOR, loc=0.0, scale=1.0)


def test_predictive_t_rejects_nonpositive_scale() -> None:
    with pytest.raises(ValueError, match="scale"):
        PredictiveT(nu=4.0, loc=0.0, scale=0.0)


def test_predictive_t_interval_is_symmetric_about_loc() -> None:
    dist = PredictiveT(nu=4.0, loc=5.0, scale=2.0)
    lo, hi = dist.interval(0.90)
    assert (lo + hi) / 2.0 == pytest.approx(5.0)
    assert lo < 5.0 < hi


def test_predictive_t_interval_is_wider_than_gaussian() -> None:
    # The whole point: a fat tail must produce a wider 95% interval than 1.96*sigma.
    dist = PredictiveT(nu=4.0, loc=0.0, scale=1.0)
    lo, hi = dist.interval(0.95)
    half_width = (hi - lo) / 2.0
    assert half_width > 1.96


def test_predictive_t_cdf_matches_scipy() -> None:
    dist = PredictiveT(nu=6.0, loc=1.0, scale=3.0)
    expected = float(stats.t(df=6.0, loc=1.0, scale=3.0).cdf(4.0))
    assert dist.cdf(4.0) == pytest.approx(expected)


def test_predictive_t_ppf_is_cdf_inverse() -> None:
    dist = PredictiveT(nu=5.0, loc=2.0, scale=1.5)
    assert dist.cdf(dist.ppf(0.3)) == pytest.approx(0.3)


def test_predictive_t_sample_is_reproducible_and_located() -> None:
    dist = PredictiveT(nu=8.0, loc=10.0, scale=2.0)
    draws_a = dist.sample(np.random.default_rng(42), size=10000)
    draws_b = dist.sample(np.random.default_rng(42), size=10000)
    assert np.array_equal(draws_a, draws_b)            # same seed -> same stream
    assert draws_a.shape == (10000,)
    assert float(np.mean(draws_a)) == pytest.approx(10.0, abs=0.2)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `py -m pytest tests/unit/common/test_student_t.py -v`
Expected: collection FAIL — `ImportError: cannot import name 'PredictiveT'` (the updated import line references a name not yet defined; this is the expected red state).

- [ ] **Step 3: Implement `PredictiveT`**

Append to `src/common/student_t.py`:

```python
@dataclass(frozen=True)
class PredictiveT:
    """A frozen Student-t predictive distribution: t(nu) shifted/scaled to (loc, scale)."""

    nu: float
    loc: float
    scale: float

    def __post_init__(self) -> None:
        if not (self.nu > NU_FLOOR):
            raise ValueError(
                f"nu must be > {NU_FLOOR} for finite variance, got {self.nu}"
            )
        if not (self.scale > 0.0) or not math.isfinite(self.scale):
            raise ValueError(f"scale must be finite and positive, got {self.scale}")

    def _frozen(self) -> "stats.rv_frozen":
        return stats.t(df=self.nu, loc=self.loc, scale=self.scale)

    def sample(self, rng: np.random.Generator, size: int | tuple[int, ...]) -> np.ndarray:
        # Draw standard-t via the caller's Generator, then apply location-scale.
        # Keeps the caller's RNG stream (unlike scipy's .rvs).
        return self.loc + self.scale * rng.standard_t(self.nu, size=size)

    def interval(self, level: float) -> tuple[float, float]:
        lo, hi = self._frozen().interval(level)
        return float(lo), float(hi)

    def cdf(self, x: float) -> float:
        return float(self._frozen().cdf(x))

    def ppf(self, q: float) -> float:
        return float(self._frozen().ppf(q))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `py -m pytest tests/unit/common/test_student_t.py -v`
Expected: PASS (all Task 1 + Task 2 tests)

- [ ] **Step 5: Commit**

```bash
git add src/common/student_t.py tests/unit/common/test_student_t.py
git commit -m "feat(student-t): add PredictiveT scipy-backed distribution wrapper"
```

---

## Task 3: `predictive_t()` factory (composition + invariant + validation)

**Files:**
- Modify: `src/common/student_t.py`
- Test: `tests/unit/common/test_student_t.py`

- [ ] **Step 1: Add the failing tests for the factory**

First, update the import block at the top of `tests/unit/common/test_student_t.py` to add the factory function:

```python
from src.common.student_t import (
    FormulaRule,
    HybridRule,
    NU_FLOOR,
    PredictiveT,
    predictive_t,
)
from scipy import stats
```

Then append these tests:

```python
def test_predictive_t_scale_inflation() -> None:
    # Epistemic uncertainty inflates scale by sqrt(1 + 1/n_eff).
    dist = predictive_t(
        mu=0.0, sigma=2.0, n_eff=3.0, nu_loss=4.0, rule=FormulaRule()
    )
    assert dist.scale == pytest.approx(2.0 * math.sqrt(1.0 + 1.0 / 3.0))
    assert dist.loc == 0.0


def test_predictive_t_rejects_zero_n_eff() -> None:
    # No silent n_eff = infinity AND no n_eff = 0 (scale would blow up).
    with pytest.raises(ValueError, match="n_eff"):
        predictive_t(mu=0.0, sigma=1.0, n_eff=0.0, nu_loss=4.0, rule=FormulaRule())


def test_predictive_t_rejects_nonpositive_sigma() -> None:
    with pytest.raises(ValueError, match="sigma"):
        predictive_t(mu=0.0, sigma=0.0, n_eff=5.0, nu_loss=4.0, rule=FormulaRule())


def test_predictive_t_never_thinner_than_nu_loss() -> None:
    # The invariant: across all sample sizes, nu_pred <= nu_loss.
    rule = FormulaRule()
    for n_eff in (0.01, 0.5, 1.0, 4.0, 10.0, 1000.0):
        dist = predictive_t(mu=0.0, sigma=1.0, n_eff=n_eff, nu_loss=4.0, rule=rule)
        assert dist.nu <= 4.0 + 1e-9


def test_predictive_t_fattens_as_data_shrinks() -> None:
    # Smaller n_eff -> smaller nu (fatter tail) -> wider interval.
    rule = FormulaRule()
    rich = predictive_t(mu=0.0, sigma=1.0, n_eff=1000.0, nu_loss=4.0, rule=rule)
    poor = predictive_t(mu=0.0, sigma=1.0, n_eff=0.2, nu_loss=4.0, rule=rule)
    assert poor.nu < rich.nu
    rich_lo, rich_hi = rich.interval(0.95)
    poor_lo, poor_hi = poor.interval(0.95)
    assert (poor_hi - poor_lo) > (rich_hi - rich_lo)


def test_predictive_t_passes_nu_fit_through_to_rule() -> None:
    # The factory must forward nu_fit so HybridRule can use it.
    rule = HybridRule(nu_prior=2.5, k=1.0, tau=10.0)
    without = predictive_t(
        mu=0.0, sigma=1.0, n_eff=10.0, nu_loss=20.0, rule=rule
    )
    with_fit = predictive_t(
        mu=0.0, sigma=1.0, n_eff=10.0, nu_loss=20.0, rule=rule, nu_fit=8.0
    )
    assert without.nu != with_fit.nu
    assert with_fit.nu == pytest.approx(10.25)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `py -m pytest tests/unit/common/test_student_t.py -v`
Expected: collection FAIL — `ImportError: cannot import name 'predictive_t'` (the updated import line references the not-yet-defined factory; expected red state).

- [ ] **Step 3: Implement the factory**

Append to `src/common/student_t.py`:

```python
def predictive_t(
    mu: float,
    sigma: float,
    n_eff: float,
    *,
    nu_loss: float,
    rule: TailRule,
    nu_fit: float | None = None,
) -> PredictiveT:
    """Build the sample-adaptive predictive Student-t.

    Args:
        mu: Point estimate (location).
        sigma: Learned/calibrated scale of the estimate.
        n_eff: EFFECTIVE number of independent observations behind sigma. Never a
            raw row count, and never omitted (no silent n_eff = infinity). Must be
            finite and > 0.
        nu_loss: The fixed aleatoric loss nu (the heavy-tail floor of the world).
        rule: Tail rule mapping (nu_loss, n_eff) -> predictive nu.
        nu_fit: Optional per-task MLE nu estimate, used by HybridRule.

    Returns:
        A PredictiveT with nu in (NU_FLOOR, nu_loss] and scale inflated by the
        epistemic factor sqrt(1 + 1/n_eff).
    """
    if not math.isfinite(n_eff) or n_eff <= 0.0:
        raise ValueError(
            f"n_eff must be a finite positive effective count, got {n_eff}"
        )
    if not (sigma > 0.0) or not math.isfinite(sigma):
        raise ValueError(f"sigma must be finite and positive, got {sigma}")
    if not (nu_loss > NU_FLOOR):
        raise ValueError(f"nu_loss must be > {NU_FLOOR}, got {nu_loss}")

    nu = rule.nu(nu_loss=nu_loss, n_eff=n_eff, nu_fit=nu_fit)
    scale = sigma * math.sqrt(1.0 + 1.0 / n_eff)
    return PredictiveT(nu=nu, loc=mu, scale=scale)
```

- [ ] **Step 4: Run the full module test suite to verify it passes**

Run: `py -m pytest tests/unit/common/test_student_t.py -v`
Expected: PASS (all tasks' tests)

- [ ] **Step 5: Commit**

```bash
git add src/common/student_t.py tests/unit/common/test_student_t.py
git commit -m "feat(student-t): add predictive_t factory composing aleatoric + epistemic tails"
```

---

## Task 4: Module exports and full-suite regression check

**Files:**
- Modify: `src/common/student_t.py`
- Test: (none new — verification only)

- [ ] **Step 1: Add an explicit public API surface**

At the top of `src/common/student_t.py`, immediately after the module docstring and before the imports' use, add an `__all__` so consumers import from one obvious surface. Insert this right after the `NU_FLOOR` definition:

```python
__all__ = [
    "NU_FLOOR",
    "TailRule",
    "FormulaRule",
    "HybridRule",
    "PredictiveT",
    "predictive_t",
]
```

- [ ] **Step 2: Verify the module imports cleanly**

Run: `py -c "from src.common.student_t import predictive_t, FormulaRule, HybridRule, PredictiveT, NU_FLOOR; print('ok')"`
Expected: prints `ok`

- [ ] **Step 3: Run the full unit suite to confirm no regressions**

Run: `py -m pytest tests/unit/common/ -v`
Expected: PASS

Then confirm nothing else broke (the module is new and imported nowhere yet, so this should be green):

Run: `py -m pytest tests/unit -q`
Expected: PASS (no new failures introduced)

- [ ] **Step 4: Commit**

```bash
git add src/common/student_t.py
git commit -m "feat(student-t): export public API surface for predictive_t module"
```

---

## Self-Review Notes (for the implementer)

- **Spec coverage:** This plan implements the spec's "New: `src/common/student_t.py`" component, the two tail rules (Fork 2), the composition + invariant (Fork 1 + "The invariant"), and the Phase 0 default parameters (`nu_prior=2.5`, `k=1.0`, `tau=10.0`). The `n_eff` validation enforces the spec's "no silent `n_eff = ∞`" rule (and additionally forbids `n_eff = 0`, which would make scale inflation diverge). Phases 1–4 are explicitly out of this plan and each gets its own.
- **Not in scope here:** the calibration harness (Phase 1), any call-site migration (Phases 2–3), and rule tuning (Phase 4). `nu_fit` is wired through the factory now so HybridRule is ready, but no MLE fitting is implemented until Phase 4 needs it.
- **Type consistency:** `predictive_t(mu, sigma, n_eff, *, nu_loss, rule, nu_fit=None)` and `rule.nu(*, nu_loss, n_eff, nu_fit=None)` use identical keyword names throughout. `PredictiveT(nu, loc, scale)` field names are stable across all tasks.

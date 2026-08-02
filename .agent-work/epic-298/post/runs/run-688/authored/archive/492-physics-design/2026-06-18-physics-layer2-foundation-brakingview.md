# Physics Layer 2 — Foundation + BrakingView Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the reusable Layer-2 scaffolding (prior-injectable parameters, braking-arc identification, terrain-gradient join, the MAP view base) and the first physics view — `BrakingView` — fitting a de-conflated, terrain-corrected braking frontier `a_brake(v) = a_b + b_b·v²` with full covariance, validated visually on Spa 2023 Q (Red Bull, both cars pooled).

**Architecture:** A new isolated package `src/physics/layer2/` that consumes the existing smoother→processed-telemetry chain and the landed #497 terrain profile. Each view solves a MAP: a frontier-binned weighted least-squares with an injectable Gaussian prior on the solved parameters and delta-method inflation from supporting-parameter uncertainty. The existing `ParameterEstimator`/`fit_braking_frontier` are left untouched as reference (spec non-goal). This plan is **Plan 1 of a series**: Plans 2–6 add the other five views on this scaffolding; Plan 7 builds the `SessionEstimator` outer round loop and the `kind=3` Matérn feedback (issue #498 proper). The `kind=3` smoother extension is **not** in this plan — a single view at round 0 does not exercise it.

**Tech Stack:** Python 3.14 (invoke as `py`), numpy, scipy (`scipy.spatial.cKDTree`, `scipy.linalg`), pandas, matplotlib (Agg backend), pytest, FastF1 (only via the existing load chain in `src/physics/session_fit.py`).

## Global Constraints

- Python is invoked as `py` (Python Launcher), never `python`. Tests: `py -m pytest tests/...`.
- The SQLite DB / FastF1 cache is the data source; analysis code must not make new FastF1 network calls. Session loading goes through the existing `load_quali_session` (offline cache) chain only.
- Mass: `MASS_KG = 808.0` (import from `src.physics.longitudinal_fit`). Gravity: `g = 9.81 m/s²`.
- Air density `rho`: the real per-session value from `load_quali_session` (measured weather). Never hard-code `1.2` in fits.
- All new modules live under `src/physics/layer2/`. Do **not** modify `parameter_estimator.py`, `braking_fit.py`, or `physics_data_models.py` except where a task explicitly says so (only `terrain.py` gets an additive, backward-compatible extension).
- Plots: `matplotlib.use("Agg")` at import; output to `reports/physics/`; `Path(out).parent.mkdir(parents=True, exist_ok=True)`; `fig.savefig(out, dpi=130, bbox_inches="tight")`; no `plt.show()`.
- Commit messages follow repo convention: `feat(physics): … (#496)` / `test(physics): … (#496)`, and end with the repo's `Co-Authored-By:` / `Claude-Session:` trailers.
- Test home: `tests/unit/physics/layer2/` (create `__init__.py` if the package convention requires it — check a sibling test dir first).

---

## File Structure

**Create:**
- `src/physics/layer2/__init__.py` — package marker; re-exports the public API.
- `src/physics/layer2/params.py` — `ParamPrior` (scalar Gaussian prior), `GaussianPrior2` (2-vector mean + 2×2 covariance), cold-start prior builders. The injectable-prior seam.
- `src/physics/layer2/arcs.py` — `BrakingArc` dataclass + `identify_braking_arcs` (contiguous `straight_brake` runs) + frontier filter.
- `src/physics/layer2/braking_view.py` — `BrakingViewResult` + `BrakingView.fit` (the de-conflated MAP).
- `src/physics/layer2/session_braking.py` — `run_braking_view_on_session` (Spa 2023 Q, both RBR cars pooled → samples + terrain → BrakingView).
- `scripts/plot_braking_view.py` — the three visual-confirmation plots.

**Modify (additive, backward-compatible):**
- `src/physics/terrain.py` — add `x_m`, `y_m` (centerline coords) to `build_terrain_profile`'s output dict; add public `gradient_at_positions(px, py, profile)`.

**Test:**
- `tests/unit/physics/layer2/test_params.py`
- `tests/unit/physics/layer2/test_terrain_join.py`
- `tests/unit/physics/layer2/test_arcs.py`
- `tests/unit/physics/layer2/test_braking_view.py`

---

## Task 0: Prior-injection types (`params.py`)

The seam every view shares: a scalar Gaussian prior and a 2-parameter Gaussian prior, with "cold-start" (wide) and "pinned" (tight) both expressed through the same type. Cold-start later becomes a sibling-view posterior with no interface change.

**Files:**
- Create: `src/physics/layer2/__init__.py`
- Create: `src/physics/layer2/params.py`
- Test: `tests/unit/physics/layer2/test_params.py`

**Interfaces:**
- Produces:
  - `ParamPrior(mu: float, sigma: float)` with `.precision -> float` (= `1/sigma²`); raises `ValueError` if `sigma <= 0`.
  - `GaussianPrior2(mu: np.ndarray, cov: np.ndarray)` (`mu` shape `(2,)`, `cov` shape `(2,2)`), with `.precision() -> np.ndarray` (= `inv(cov)`), and classmethod `cold(mu=(0.0, 0.0), scale=1e6) -> GaussianPrior2` (diagonal `scale²` covariance — effectively uninformative).
  - `cold_start_braking_supporting(cda_closed_mu: float, theta_R_mu: float, cda_rel_sigma: float = 0.5, theta_R_sigma: float = 0.3) -> dict[str, ParamPrior]` returning `{"cda_closed": ParamPrior(cda_closed_mu, cda_rel_sigma*cda_closed_mu), "theta_R": ParamPrior(theta_R_mu, theta_R_sigma)}`.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/physics/layer2/test_params.py
import numpy as np
import pytest

from src.physics.layer2.params import ParamPrior, GaussianPrior2, cold_start_braking_supporting


def test_param_prior_precision_is_inverse_variance():
    p = ParamPrior(mu=2.0, sigma=0.5)
    assert p.precision == pytest.approx(1.0 / 0.25)


def test_param_prior_rejects_nonpositive_sigma():
    with pytest.raises(ValueError):
        ParamPrior(mu=1.0, sigma=0.0)


def test_gaussian_prior2_precision_is_matrix_inverse():
    cov = np.array([[4.0, 0.0], [0.0, 0.25]])
    g = GaussianPrior2(mu=np.array([1.0, 2.0]), cov=cov)
    np.testing.assert_allclose(g.precision(), np.array([[0.25, 0.0], [0.0, 4.0]]))


def test_gaussian_prior2_cold_is_near_zero_precision():
    g = GaussianPrior2.cold()
    # Uninformative: precision entries are tiny, mean is origin.
    assert np.all(np.abs(g.precision()) < 1e-6)
    np.testing.assert_allclose(g.mu, np.array([0.0, 0.0]))


def test_cold_start_supporting_uses_relative_cda_sigma():
    s = cold_start_braking_supporting(cda_closed_mu=1.2, theta_R_mu=0.15)
    assert s["cda_closed"].mu == pytest.approx(1.2)
    assert s["cda_closed"].sigma == pytest.approx(0.6)   # 0.5 * 1.2
    assert s["theta_R"].mu == pytest.approx(0.15)
    assert s["theta_R"].sigma == pytest.approx(0.3)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/unit/physics/layer2/test_params.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.physics.layer2'`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/physics/layer2/__init__.py
"""Physics Layer 2 — arc-based frontier fitting with injectable priors (#496)."""
from src.physics.layer2.params import (
    ParamPrior,
    GaussianPrior2,
    cold_start_braking_supporting,
)

__all__ = ["ParamPrior", "GaussianPrior2", "cold_start_braking_supporting"]
```

```python
# src/physics/layer2/params.py
"""Injectable Gaussian priors for Layer-2 views (#496).

A solved parameter and a supporting parameter share ONE prior type: cold-start is
a wide sigma, pinned is a tight sigma from a cross-session/sibling-view posterior.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ParamPrior:
    """Scalar Gaussian prior (value, sigma) on a single physics parameter."""

    mu: float
    sigma: float

    def __post_init__(self) -> None:
        if self.sigma <= 0:
            raise ValueError(f"sigma must be positive; got {self.sigma!r}")

    @property
    def precision(self) -> float:
        return 1.0 / (self.sigma * self.sigma)


@dataclass(frozen=True)
class GaussianPrior2:
    """Gaussian prior on a 2-parameter vector (mean + 2x2 covariance)."""

    mu: np.ndarray
    cov: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(self, "mu", np.asarray(self.mu, dtype=float).reshape(2))
        object.__setattr__(self, "cov", np.asarray(self.cov, dtype=float).reshape(2, 2))

    def precision(self) -> np.ndarray:
        return np.linalg.inv(self.cov)

    @classmethod
    def cold(cls, mu: tuple[float, float] = (0.0, 0.0), scale: float = 1e6) -> "GaussianPrior2":
        return cls(mu=np.asarray(mu, dtype=float), cov=np.eye(2) * (scale * scale))


def cold_start_braking_supporting(
    cda_closed_mu: float,
    theta_R_mu: float,
    cda_rel_sigma: float = 0.5,
    theta_R_sigma: float = 0.3,
) -> dict[str, ParamPrior]:
    """Wide cold-start supporting priors for BrakingView.

    cda_closed is given a RELATIVE sigma (multiplicative uncertainty on drag area);
    theta_R an absolute sigma in m/s^2.
    """
    return {
        "cda_closed": ParamPrior(mu=cda_closed_mu, sigma=cda_rel_sigma * cda_closed_mu),
        "theta_R": ParamPrior(mu=theta_R_mu, sigma=theta_R_sigma),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -m pytest tests/unit/physics/layer2/test_params.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add src/physics/layer2/__init__.py src/physics/layer2/params.py tests/unit/physics/layer2/test_params.py
git commit -m "feat(physics): Layer-2 injectable Gaussian prior types (#496)"
```

---

## Task 1: Terrain-gradient join (`terrain.py` extension)

`build_terrain_profile` returns `distance_m`/`theta_rad` keyed on the pooled centerline, but **not** the centerline X/Y, so a lap's per-sample `(px, py)` can't be mapped onto it. Add the centerline coords to the output (it already computes them as `x_med`/`y_med`) and a public projection helper that returns the gradient angle at each lap sample.

**Files:**
- Modify: `src/physics/terrain.py` (add `x_m`/`y_m` to the return dict at the `return {…}` block ~line 113; add `gradient_at_positions`)
- Test: `tests/unit/physics/layer2/test_terrain_join.py`

**Interfaces:**
- Consumes: `build_terrain_profile(laps_xyz, …) -> dict` (existing).
- Produces:
  - `build_terrain_profile(...)` dict now also contains `"x_m"`, `"y_m"` (float64 arrays, length `n_grid`) — the smoothed centerline coordinates.
  - `gradient_at_positions(px: np.ndarray, py: np.ndarray, profile: dict) -> np.ndarray` — for each `(px[i], py[i])`, the centerline `theta_rad` at the nearest centerline point. Returns shape `(len(px),)` radians.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/physics/layer2/test_terrain_join.py
import numpy as np

from src.physics.terrain import build_terrain_profile, gradient_at_positions


def _ramp_oval_laps(n_pts=400, n_laps=5, radius=200.0, grade=0.05):
    """Closed oval in XY with a deterministic altitude ramp -> known gradient sign."""
    t = np.linspace(0.0, 2.0 * np.pi, n_pts, endpoint=False)
    x = radius * np.cos(t)
    y = radius * np.sin(t)
    # altitude rises on the first half of the lap (z = grade * along-distance-ish)
    z = grade * (radius * t)  # monotone in t over [0, 2pi)
    laps = [(x.copy(), y.copy(), z.copy()) for _ in range(n_laps)]
    return laps


def test_build_terrain_profile_exposes_centerline_xy():
    laps = _ramp_oval_laps()
    prof = build_terrain_profile(laps, n_grid=300, min_laps=3)
    assert "x_m" in prof and "y_m" in prof
    assert prof["x_m"].shape == prof["distance_m"].shape
    # centerline lies on the oval radius
    r = np.hypot(prof["x_m"], prof["y_m"])
    assert np.allclose(r, 200.0, atol=5.0)


def test_gradient_at_positions_matches_nearest_centerline():
    laps = _ramp_oval_laps(grade=0.05)
    prof = build_terrain_profile(laps, n_grid=300, min_laps=3)
    # query the same oval points
    t = np.linspace(0.0, 2.0 * np.pi, 50, endpoint=False)
    px = 200.0 * np.cos(t)
    py = 200.0 * np.sin(t)
    theta = gradient_at_positions(px, py, prof)
    assert theta.shape == (50,)
    # uphill ramp -> positive gradient angle on average, bounded by atan(grade)
    assert np.nanmedian(theta) > 0.0
    assert np.nanmax(np.abs(theta)) < np.arctan(0.05) + 0.05
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/unit/physics/layer2/test_terrain_join.py -v`
Expected: FAIL — `ImportError: cannot import name 'gradient_at_positions'` (and `KeyError 'x_m'` once import is added).

- [ ] **Step 3: Add `x_m`/`y_m` to the return dict**

In `src/physics/terrain.py`, in `build_terrain_profile`, extend the `return {…}` dict (currently starting `"distance_m": distance,`) to include the centerline coords already computed as `x_med`/`y_med`:

```python
    return {
        "distance_m": distance,
        "x_m": x_med.astype(np.float64),
        "y_m": y_med.astype(np.float64),
        "altitude_m": z_med.astype(np.float64),
        "grade": grade.astype(np.float64),
        "theta_rad": np.arctan(grade).astype(np.float64),
        "bank_rad": bank["bank_rad"],
        "bank_available": bank["bank_available"],
        "bank_lateral_span_m": bank["bank_lateral_span_m"],
        "bank_residual_rmse_m": bank["bank_residual_rmse_m"],
        "altitude_uncertainty_m": _robust_altitude_scatter(z_stack).astype(np.float64),
    }
```

- [ ] **Step 4: Add the public projection helper**

Append to `src/physics/terrain.py`:

```python
def gradient_at_positions(
    px: np.ndarray,
    py: np.ndarray,
    profile: dict[str, np.ndarray],
) -> np.ndarray:
    """Gradient angle theta(s) at each lap sample, by nearest-centerline projection.

    Each (px[i], py[i]) is matched to the nearest pooled-centerline point and
    assigned that point's ``theta_rad``.  Robust to the racing line differing from
    the centerline (projection, not arc-length matching).  Returns radians.
    """
    from scipy.spatial import cKDTree

    px = np.asarray(px, dtype=float)
    py = np.asarray(py, dtype=float)
    center = np.column_stack([profile["x_m"], profile["y_m"]])
    tree = cKDTree(center)
    _, idx = tree.query(np.column_stack([px, py]))
    return profile["theta_rad"][idx]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `py -m pytest tests/unit/physics/layer2/test_terrain_join.py -v`
Expected: PASS (2 tests).

- [ ] **Step 6: Confirm no regression on terrain tests**

Run: `py -m pytest tests/unit/physics/test_terrain.py -v`
Expected: PASS (existing terrain suite still green — the change is additive).

- [ ] **Step 7: Commit**

```bash
git add src/physics/terrain.py tests/unit/physics/layer2/test_terrain_join.py
git commit -m "feat(physics): expose centerline XY + gradient_at_positions on terrain profile (#496)"
```

---

## Task 2: Braking-arc identification (`arcs.py`)

Group contiguous `straight_brake`-regime samples into arcs and keep only the frontier arcs (the ones that actually push the limit). The regime label is produced upstream by `SegmentClassifier`; in this view we operate on already-classified `KinematicSample`s (each has `.regime`).

**Files:**
- Create: `src/physics/layer2/arcs.py`
- Test: `tests/unit/physics/layer2/test_arcs.py`

**Interfaces:**
- Consumes: `KinematicSample` (from `src.physics.physics_data_models`) — fields used: `.regime: str`, `.speed: float`, `.a_longitudinal: float`, `.timestamp_ms: int`.
- Produces:
  - `BrakingArc(sample_indices: list[int], peak_decel: float, mean_speed: float)` (frozen dataclass).
  - `identify_braking_arcs(samples: Sequence[KinematicSample], min_len: int = 3, frontier_decel_quantile: float = 0.6) -> list[BrakingArc]` — contiguous runs of `regime == "straight_brake"` with `>= min_len` samples; keeps arcs whose `peak_decel` (= `max(-a_longitudinal)` over the arc) is at or above the `frontier_decel_quantile` of all candidate arcs' peak decel. Non-frontier arcs are dropped from the returned list.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/physics/layer2/test_arcs.py
import numpy as np

from src.physics.layer2.arcs import BrakingArc, identify_braking_arcs


class _FakeSample:
    """Minimal stand-in carrying only the fields identify_braking_arcs reads."""
    def __init__(self, regime, speed, a_long, ts):
        self.regime = regime
        self.speed = speed
        self.a_longitudinal = a_long
        self.timestamp_ms = ts


def _seq(specs):
    out, ts = [], 0
    for regime, speed, a_long in specs:
        out.append(_FakeSample(regime, speed, a_long, ts))
        ts += 100
    return out


def test_contiguous_brake_runs_become_arcs():
    samples = _seq(
        [("straight_throttle", 80, 2.0)] * 3
        + [("straight_brake", 80, -5.0), ("straight_brake", 70, -5.2), ("straight_brake", 60, -4.8)]
        + [("corner", 55, -0.5)] * 2
        + [("straight_brake", 90, -1.0), ("straight_brake", 88, -1.1), ("straight_brake", 86, -0.9)]
    )
    arcs = identify_braking_arcs(samples, min_len=3, frontier_decel_quantile=0.0)
    assert len(arcs) == 2
    assert isinstance(arcs[0], BrakingArc)
    assert arcs[0].peak_decel == 5.2  # max(-a_long) over first run


def test_frontier_filter_drops_gentle_arcs():
    samples = _seq(
        [("straight_brake", 80, -5.0), ("straight_brake", 70, -5.2), ("straight_brake", 60, -4.8)]
        + [("straight_throttle", 60, 1.0)]
        + [("straight_brake", 90, -1.0), ("straight_brake", 88, -1.1), ("straight_brake", 86, -0.9)]
    )
    arcs = identify_braking_arcs(samples, min_len=3, frontier_decel_quantile=0.6)
    # only the hard-braking arc (peak 5.2) survives the 0.6-quantile cut
    assert len(arcs) == 1
    assert arcs[0].peak_decel == 5.2


def test_short_runs_are_ignored():
    samples = _seq(
        [("straight_brake", 80, -5.0), ("straight_brake", 70, -5.2)]  # len 2 < min_len
        + [("straight_throttle", 60, 1.0)]
    )
    arcs = identify_braking_arcs(samples, min_len=3)
    assert arcs == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/unit/physics/layer2/test_arcs.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.physics.layer2.arcs'`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/physics/layer2/arcs.py
"""Braking-arc identification + frontier filter for Layer 2 (#496)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

_BRAKE_REGIME = "straight_brake"


@dataclass(frozen=True)
class BrakingArc:
    """A contiguous braking event: indices into the source sample list."""

    sample_indices: list[int]
    peak_decel: float   # max(-a_longitudinal) over the arc, m/s^2
    mean_speed: float   # mean speed over the arc, m/s


def _contiguous_runs(samples: Sequence, min_len: int) -> list[list[int]]:
    runs: list[list[int]] = []
    cur: list[int] = []
    for i, s in enumerate(samples):
        if s.regime == _BRAKE_REGIME:
            cur.append(i)
        else:
            if len(cur) >= min_len:
                runs.append(cur)
            cur = []
    if len(cur) >= min_len:
        runs.append(cur)
    return runs


def identify_braking_arcs(
    samples: Sequence,
    min_len: int = 3,
    frontier_decel_quantile: float = 0.6,
) -> list[BrakingArc]:
    """Contiguous straight_brake runs, filtered to the frontier (hardest) arcs.

    An arc's peak_decel is max(-a_longitudinal) over its samples.  Arcs with peak
    below the ``frontier_decel_quantile`` of all candidate peaks are dropped
    (gentle, non-limit braking is not capability evidence).
    """
    runs = _contiguous_runs(samples, min_len)
    if not runs:
        return []
    candidates: list[BrakingArc] = []
    for run in runs:
        decels = [-samples[i].a_longitudinal for i in run]
        speeds = [samples[i].speed for i in run]
        candidates.append(
            BrakingArc(
                sample_indices=run,
                peak_decel=float(max(decels)),
                mean_speed=float(np.mean(speeds)),
            )
        )
    peaks = np.array([a.peak_decel for a in candidates])
    cut = float(np.quantile(peaks, frontier_decel_quantile))
    return [a for a in candidates if a.peak_decel >= cut]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -m pytest tests/unit/physics/layer2/test_arcs.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add src/physics/layer2/arcs.py tests/unit/physics/layer2/test_arcs.py
git commit -m "feat(physics): Layer-2 braking-arc identification + frontier filter (#496)"
```

---

## Task 3: BrakingView — the de-conflated MAP fit (`braking_view.py`)

The core. From frontier braking samples, isolate **pure** braking capability by subtracting the supporting drag/rolling/terrain off the measured decel, bin by speed, then solve a Bayesian linear regression with an injectable prior and delta-method inflation from the supporting-prior uncertainty.

Per sample (deceleration positive): `decel_total = -a_longitudinal`. Longitudinal balance gives
`a_brake_obs = decel_total - CdA·ρ·v²/(2m) - θ_R - g·sin θ(s)`.
Fit `a_brake_obs = a_b + b_b·v²`. Supporting-prior inflation (delta method):
`Var_support(v) = (ρ v²/2m)² σ_CdA² + σ_θR²`. MAP posterior:
`Σ_post = (XᵀWX + Λ)⁻¹`, `μ_post = Σ_post (XᵀW d + Λ μ_prior)`, with `W = diag(1/(s² + Var_support))`, `Λ = Σ_prior⁻¹`.

**Files:**
- Create: `src/physics/layer2/braking_view.py`
- Test: `tests/unit/physics/layer2/test_braking_view.py`

**Interfaces:**
- Consumes: `KinematicSample` (`.speed`, `.a_longitudinal`); `ParamPrior`, `GaussianPrior2` (Task 0); a per-sample gradient array `theta_per_sample` (Task 1, radians).
- Produces:
  - `BrakingViewResult` (frozen): `a_b`, `b_b` (float), `covariance` (2×2), `bin_speeds`, `bin_decel_obs`, `bin_var` (np arrays), `n_bins`, `n_samples`, `prior: GaussianPrior2`, method `a_brake(v) -> float` and `to_braking_parameters() -> BrakingParameters`.
  - `BrakingView.fit(samples, theta_per_sample, *, cda_closed: ParamPrior, theta_R: ParamPrior, mass_kg: float, rho: float, prior: GaussianPrior2, g: float = 9.81, quantile: float = 0.95, v_lo_ms: float = 15.0, v_hi_ms: float = 96.0, step_ms: float = 8.0, min_pts_per_bin: int = 8, min_bins: int = 4) -> Optional[BrakingViewResult]`.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/physics/layer2/test_braking_view.py
import numpy as np
import pytest

from src.physics.layer2.params import ParamPrior, GaussianPrior2
from src.physics.layer2.braking_view import BrakingView, BrakingViewResult


class _FakeSample:
    def __init__(self, speed, a_long):
        self.speed = speed
        self.a_longitudinal = a_long


def _synth_brake_samples(a_b, b_b, cda, theta_R, mass, rho, theta_grad, n=4000, seed=0):
    """Generate brake samples whose TOTAL decel includes braking + drag + rolling + gravity.

    measured decel_total = a_brake(v) + CdA*rho*v^2/(2m) + theta_R + g*sin(theta)
    a_longitudinal = -decel_total ; speeds spread 20..90 m/s with mild scatter.
    """
    rng = np.random.default_rng(seed)
    v = rng.uniform(20.0, 90.0, n)
    a_brake = a_b + b_b * v ** 2
    drag = cda * rho * v ** 2 / (2.0 * mass)
    decel_total = a_brake + drag + theta_R + 9.81 * np.sin(theta_grad)
    decel_total += rng.normal(0.0, 0.15, n)  # small scatter below the frontier
    samples = [_FakeSample(float(vi), float(-di)) for vi, di in zip(v, decel_total)]
    theta = np.full(n, theta_grad)
    return samples, theta


def test_recovers_true_braking_params_when_supporting_priors_correct():
    a_b, b_b, cda, theta_R, mass, rho = 14.0, 0.0009, 1.2, 0.15, 808.0, 1.18
    samples, theta = _synth_brake_samples(a_b, b_b, cda, theta_R, mass, rho, theta_grad=0.0)
    res = BrakingView.fit(
        samples, theta,
        cda_closed=ParamPrior(cda, 0.01 * cda),
        theta_R=ParamPrior(theta_R, 0.01),
        mass_kg=mass, rho=rho,
        prior=GaussianPrior2.cold(),
    )
    assert isinstance(res, BrakingViewResult)
    assert res.b_b > 0.0                       # aero braking is POSITIVE (the headline)
    assert res.a_b == pytest.approx(a_b, abs=1.0)
    assert res.b_b == pytest.approx(b_b, abs=3e-4)


def test_ignoring_drag_inflates_b_b_the_conflation_bug():
    """With CdA forced to 0, the drag v^2 term leaks into b_b -> biased high."""
    a_b, b_b, cda, theta_R, mass, rho = 14.0, 0.0009, 1.2, 0.15, 808.0, 1.18
    samples, theta = _synth_brake_samples(a_b, b_b, cda, theta_R, mass, rho, theta_grad=0.0)
    res = BrakingView.fit(
        samples, theta,
        cda_closed=ParamPrior(1e-9, 1e-9),     # pretend zero drag
        theta_R=ParamPrior(theta_R, 0.01),
        mass_kg=mass, rho=rho,
        prior=GaussianPrior2.cold(),
    )
    # b_b absorbs ~ rho/(2m) = 1.18/1616 ~ 7.3e-4 on top of the true 9e-4
    assert res.b_b > b_b + 3e-4


def test_uphill_gradient_correction_changes_a_b():
    """Same braking, +4% uphill: ignoring it (theta=0) biases the fit vs correcting it."""
    a_b, b_b, cda, theta_R, mass, rho = 14.0, 0.0009, 1.2, 0.15, 808.0, 1.18
    grad = np.arctan(0.04)
    samples, theta = _synth_brake_samples(a_b, b_b, cda, theta_R, mass, rho, theta_grad=grad)
    corrected = BrakingView.fit(
        samples, theta,
        cda_closed=ParamPrior(cda, 0.01 * cda), theta_R=ParamPrior(theta_R, 0.01),
        mass_kg=mass, rho=rho, prior=GaussianPrior2.cold(),
    )
    flat = BrakingView.fit(
        samples, np.zeros_like(theta),         # WRONG: assume flat
        cda_closed=ParamPrior(cda, 0.01 * cda), theta_R=ParamPrior(theta_R, 0.01),
        mass_kg=mass, rho=rho, prior=GaussianPrior2.cold(),
    )
    # correcting recovers ~a_b; ignoring the uphill leaves the +g*sin(theta) ~0.39
    # m/s^2 gravity assist in a_b (intercept biased high)
    assert corrected.a_b == pytest.approx(a_b, abs=1.0)
    assert flat.a_b > corrected.a_b + 0.2


def test_supporting_prior_sigma_inflates_posterior_covariance():
    a_b, b_b, cda, theta_R, mass, rho = 14.0, 0.0009, 1.2, 0.15, 808.0, 1.18
    samples, theta = _synth_brake_samples(a_b, b_b, cda, theta_R, mass, rho, theta_grad=0.0)
    tight = BrakingView.fit(
        samples, theta, cda_closed=ParamPrior(cda, 0.01 * cda), theta_R=ParamPrior(theta_R, 0.01),
        mass_kg=mass, rho=rho, prior=GaussianPrior2.cold(),
    )
    loose = BrakingView.fit(
        samples, theta, cda_closed=ParamPrior(cda, 0.5 * cda), theta_R=ParamPrior(theta_R, 0.3),
        mass_kg=mass, rho=rho, prior=GaussianPrior2.cold(),
    )
    assert loose.covariance[1, 1] > tight.covariance[1, 1]   # b_b variance grows


def test_returns_none_on_insufficient_bins():
    samples = [_FakeSample(40.0, -5.0)] * 5    # one speed -> one bin
    res = BrakingView.fit(
        samples, np.zeros(5),
        cda_closed=ParamPrior(1.2, 0.6), theta_R=ParamPrior(0.15, 0.3),
        mass_kg=808.0, rho=1.18, prior=GaussianPrior2.cold(), min_bins=4,
    )
    assert res is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/unit/physics/layer2/test_braking_view.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.physics.layer2.braking_view'`.

- [ ] **Step 3: Write the implementation**

```python
# src/physics/layer2/braking_view.py
"""BrakingView: terrain-corrected, de-conflated braking-frontier MAP fit (#496).

Model:  a_brake(v) = a_b + b_b * v^2   (pure braking capability, m/s^2)

The MEASURED deceleration includes drag, rolling and gravity; those are removed
using supporting priors and the terrain gradient BEFORE the fit, so b_b is the
true aero-braking term (not the drag v^2 term it conflates in the raw fit).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

from src.physics.layer2.params import GaussianPrior2, ParamPrior
from src.physics.physics_data_models import BrakingParameters


@dataclass(frozen=True)
class BrakingViewResult:
    a_b: float
    b_b: float
    covariance: np.ndarray
    bin_speeds: np.ndarray
    bin_decel_obs: np.ndarray
    bin_var: np.ndarray
    n_bins: int
    n_samples: int
    prior: GaussianPrior2

    def a_brake(self, v: float) -> float:
        return max(0.0, self.a_b + self.b_b * v * v)

    def to_braking_parameters(self) -> BrakingParameters:
        return BrakingParameters(a_b=self.a_b, b_b=self.b_b, covariance=self.covariance)


class BrakingView:
    """Session-combined braking-frontier view."""

    @staticmethod
    def fit(
        samples: Sequence,
        theta_per_sample: np.ndarray,
        *,
        cda_closed: ParamPrior,
        theta_R: ParamPrior,
        mass_kg: float,
        rho: float,
        prior: GaussianPrior2,
        g: float = 9.81,
        quantile: float = 0.95,
        v_lo_ms: float = 15.0,
        v_hi_ms: float = 96.0,
        step_ms: float = 8.0,
        min_pts_per_bin: int = 8,
        min_bins: int = 4,
    ) -> Optional["BrakingViewResult"]:
        v = np.array([s.speed for s in samples], dtype=float)
        a_long = np.array([s.a_longitudinal for s in samples], dtype=float)
        theta = np.asarray(theta_per_sample, dtype=float)

        brake = a_long < 0.0
        v = v[brake]
        decel_total = -a_long[brake]
        theta = theta[brake]
        if v.size == 0:
            return None

        # De-conflate: isolate pure braking capability per sample.
        drag = cda_closed.mu * rho * v ** 2 / (2.0 * mass_kg)
        a_brake_obs = decel_total - drag - theta_R.mu - g * np.sin(theta)

        # Frontier bins: per speed-bin upper-quantile of the pure-braking obs.
        bin_v: list[float] = []
        bin_d: list[float] = []
        for left in np.arange(v_lo_ms, v_hi_ms, step_ms):
            mask = (v >= left) & (v < left + step_ms)
            if int(mask.sum()) >= min_pts_per_bin:
                bin_v.append(float(v[mask].mean()))
                bin_d.append(float(np.quantile(a_brake_obs[mask], quantile)))
        if len(bin_v) < min_bins:
            return None
        vb = np.array(bin_v)
        db = np.array(bin_d)

        # Delta-method supporting-prior variance per bin (inflates obs noise).
        var_support = (rho * vb ** 2 / (2.0 * mass_kg)) ** 2 * cda_closed.sigma ** 2 \
            + theta_R.sigma ** 2

        # Intrinsic bin scatter s^2 from an initial unweighted OLS.
        X = np.column_stack([np.ones_like(vb), vb ** 2])
        coef0, *_ = np.linalg.lstsq(X, db, rcond=None)
        resid0 = db - X @ coef0
        s2 = float(np.dot(resid0, resid0) / max(len(db) - 2, 1))

        # MAP (Bayesian linear regression): Sigma_post = (X' W X + Lambda)^-1.
        w = 1.0 / (s2 + var_support)
        XtW = X.T * w
        Lambda = prior.precision()
        precision = XtW @ X + Lambda
        cov_post = np.linalg.inv(precision)
        rhs = XtW @ db + Lambda @ prior.mu
        mean_post = cov_post @ rhs

        resid = db - X @ mean_post
        return BrakingViewResult(
            a_b=float(mean_post[0]),
            b_b=float(mean_post[1]),
            covariance=cov_post,
            bin_speeds=vb,
            bin_decel_obs=db,
            bin_var=s2 + var_support,
            n_bins=len(vb),
            n_samples=int(brake.sum()),
            prior=prior,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `py -m pytest tests/unit/physics/layer2/test_braking_view.py -v`
Expected: PASS (5 tests). If `test_recovers_true_braking_params` is marginally outside tol, widen the synthetic `n` to 8000 (more samples per bin tightens the frontier quantile) — do **not** loosen the physics.

- [ ] **Step 5: Run the whole Layer-2 unit suite**

Run: `py -m pytest tests/unit/physics/layer2/ -v`
Expected: PASS (all of Tasks 0–3).

- [ ] **Step 6: Commit**

```bash
git add src/physics/layer2/braking_view.py tests/unit/physics/layer2/test_braking_view.py
git commit -m "feat(physics): BrakingView de-conflated terrain-corrected MAP fit (#496)"
```

---

## Task 4: Session orchestration — Spa 2023 Q, both RBR cars (`session_braking.py`)

Wire the real data path: load Spa 2023 Q, fit both Red Bull cars' flying laps through the existing smoother chain, classify regimes, build the terrain profile from the session's XYZ, pool both cars' braking samples, and run `BrakingView`.

**Files:**
- Create: `src/physics/layer2/session_braking.py`
- Test: (integration; no unit test — exercised by Task 6's run + smoke assert)

**Interfaces:**
- Consumes: `load_quali_session`, `driver_num`, `driver_streams`, `stint_span`, `calibrate_session_hp`, `fit_lap`, `smoother_to_processed_telemetry`, `_build_control_df` (from `session_fit.py` — import the module-level helper), `SegmentClassifier`, `build_terrain_profile`, `gradient_at_positions`, `BrakingView`, `cold_start_braking_supporting`, `GaussianPrior2`.
- Produces:
  - `SessionBrakingResult(result: BrakingViewResult, samples: list[KinematicSample], theta_per_sample: np.ndarray, rho: float, drivers: list[str], raw_p99_decel: float)`.
  - `run_braking_view_on_session(year: int = 2023, gp: str = "Belgium", drivers: tuple[str, ...] = ("VER", "PER"), cache: str | None = None) -> SessionBrakingResult`.

- [ ] **Step 1: Write the implementation**

```python
# src/physics/layer2/session_braking.py
"""Run BrakingView on a real quali session, pooling both constructor cars (#496)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.physics.layer2.braking_view import BrakingView, BrakingViewResult
from src.physics.layer2.params import GaussianPrior2, cold_start_braking_supporting
from src.physics.longitudinal_fit import MASS_KG

_FLY_FRACTION = 1.08
# Cold-start drag/rolling seeds (wide sigma). CdA ~1.2 m^2 closed-wing modern F1;
# theta_R ~0.15 m/s^2 rolling. These are intentionally loose; the loop will pin
# them later from DragView/CoastView posteriors.
_CDA0 = 1.2
_THETA_R0 = 0.15


@dataclass(frozen=True)
class SessionBrakingResult:
    result: BrakingViewResult
    samples: list
    theta_per_sample: np.ndarray
    rho: float
    drivers: list[str]
    raw_p99_decel: float


def _driver_samples(session, driver):
    """Fit one driver's flying laps -> (processed_df, control_df, raw_xyz_laps)."""
    from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span
    from src.preprocessing.trajectory.calibration import calibrate_session_hp, fit_lap
    from src.preprocessing.trajectory.physics_adapter import smoother_to_processed_telemetry
    from src.physics.session_fit import _build_control_df

    num = driver_num(session, driver)
    pos_d, spd_d = driver_streams(session, num)
    valid = session.laps.pick_drivers(driver)
    valid = valid[valid["LapTime"].notna()]
    valid = valid[valid["LapTime"].dt.total_seconds() > 50]
    if valid.empty:
        return None
    best_s = float(valid["LapTime"].dt.total_seconds().min())
    fast = valid.loc[valid["LapTime"].dt.total_seconds().idxmin()]
    flying = valid[valid["LapTime"].dt.total_seconds() <= _FLY_FRACTION * best_s]

    st0, st1, _ = stint_span(session, driver, int(fast["Stint"]), pad=2.0)
    mp = (pos_d["t"] >= st0) & (pos_d["t"] <= st1)
    mc = (spd_d["t"] >= st0) & (spd_d["t"] <= st1)
    hp = calibrate_session_hp(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp],
                              spd_d["t"][mc], spd_d["V"][mc], order=4)

    span: dict[int, tuple] = {}
    proc, ctrl, xyz = [], [], []
    for _, lap in flying.iterrows():
        sn = int(lap["Stint"])
        if sn not in span:
            s0, s1, _ = stint_span(session, driver, sn, pad=2.0)
            span[sn] = (s0, s1)
        s0, s1 = span[sn]
        t0 = float(lap["LapStartTime"].total_seconds())
        t1 = float(lap["Time"].total_seconds())
        try:
            ss, info = fit_lap(pos_d, spd_d, t0, t1, hp, overhang=8.0, bounds=(s0, s1))
            dfp = smoother_to_processed_telemetry(ss, info["lap_t"], driver_id=driver,
                                                  lap_number=int(lap["LapNumber"]))
        except Exception:
            continue
        cdf = _build_control_df(session, num, t0, t1)
        if dfp.empty or cdf.empty:
            continue
        proc.append(dfp)
        ctrl.append(cdf)
        # Terrain profile needs REAL altitude: take the raw XYZ (metres, incl. Z)
        # from the position stream over this lap window, not the 2D-smoothed px/py.
        lap_m = (pos_d["t"] >= t0) & (pos_d["t"] <= t1)
        if int(lap_m.sum()) >= 50:
            xyz.append((pos_d["X"][lap_m], pos_d["Y"][lap_m], pos_d["Z"][lap_m]))
    if not proc:
        return None
    return pd.concat(proc, ignore_index=True), pd.concat(ctrl, ignore_index=True), xyz


def _to_kinematic_samples(processed: pd.DataFrame, control: pd.DataFrame):
    """Classify processed telemetry into regime-tagged KinematicSamples."""
    from src.physics.segment_classifier import SegmentClassifier
    from src.physics.physics_data_models import ControlState

    controls = [
        ControlState(
            timestamp_ms=int(r.session_time_ms),
            throttle_confidence=1.0,
            throttle_value=float(min(max(r.throttle / 100.0, 0.0), 1.0)),
            brake_probability=float(min(max(r.brake / 100.0, 0.0), 1.0)),
            gear=int(r.gear) if not np.isnan(r.gear) else None,
            drs=bool(r.drs >= 10),
        )
        for r in control.itertuples()
    ]
    segmented = SegmentClassifier().classify_samples(processed, controls)
    return list(segmented.samples)


def run_braking_view_on_session(
    year: int = 2023,
    gp: str = "Belgium",
    drivers: tuple[str, ...] = ("VER", "PER"),
    cache: str | None = None,
) -> SessionBrakingResult:
    from src.physics.session_fit import load_quali_session, DEFAULT_CACHE
    from src.physics.terrain import build_terrain_profile, gradient_at_positions

    session, rho = load_quali_session(year, gp, "Q", cache or DEFAULT_CACHE)

    all_samples: list = []
    all_xyz: list = []
    used: list[str] = []
    for drv in drivers:
        out = _driver_samples(session, drv)
        if out is None:
            continue
        processed, control, xyz = out
        all_samples.extend(_to_kinematic_samples(processed, control))
        all_xyz.extend(xyz)
        used.append(drv)
    if not all_samples:
        raise RuntimeError(f"no usable samples for {drivers} at {gp} {year}")

    profile = build_terrain_profile(all_xyz, min_laps=3)
    px = np.array([s.position[0] for s in all_samples])
    py = np.array([s.position[1] for s in all_samples])
    theta = gradient_at_positions(px, py, profile)

    supporting = cold_start_braking_supporting(cda_closed_mu=_CDA0, theta_R_mu=_THETA_R0)
    result = BrakingView.fit(
        all_samples, theta,
        cda_closed=supporting["cda_closed"], theta_R=supporting["theta_R"],
        mass_kg=MASS_KG, rho=rho, prior=GaussianPrior2.cold(),
    )
    if result is None:
        raise RuntimeError("BrakingView returned None (insufficient frontier bins)")

    decel = np.array([-s.a_longitudinal for s in all_samples])
    raw_p99 = float(np.quantile(decel[decel > 0], 0.99))
    return SessionBrakingResult(
        result=result, samples=all_samples, theta_per_sample=theta,
        rho=rho, drivers=used, raw_p99_decel=raw_p99,
    )
```

- [ ] **Step 2: Smoke-import check**

Run: `py -c "from src.physics.layer2.session_braking import run_braking_view_on_session; print('ok')"`
Expected: prints `ok` (no import errors). This does not run a session yet (Task 6 does).

- [ ] **Step 3: Commit**

```bash
git add src/physics/layer2/session_braking.py
git commit -m "feat(physics): pool both RBR cars into BrakingView on a real session (#496)"
```

---

## Task 5: Visual confirmation suite (`scripts/plot_braking_view.py`)

The three plots you asked for, mirroring `scripts/plot_braking_frontier.py` style (Agg, `reports/physics/`, dpi=130): (1) the braking arcs, (2) the fit with its uncertainty band, (3) prior-vs-posterior.

**Files:**
- Create: `scripts/plot_braking_view.py`

**Interfaces:**
- Consumes: `run_braking_view_on_session`, `SessionBrakingResult`, `BrakingViewResult`.
- Produces (figures): `reports/physics/braking_view_arcs_{gp}_{year}.png`, `braking_view_fit_{gp}_{year}.png`, `braking_view_prior_posterior_{gp}_{year}.png`.

- [ ] **Step 1: Write the plotting script**

```python
# scripts/plot_braking_view.py
"""Visual confirmation for BrakingView (#496): arcs, fit+uncertainty, prior-vs-posterior."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.physics.layer2.arcs import identify_braking_arcs
from src.physics.layer2.session_braking import run_braking_view_on_session

_OUT = Path("reports/physics")


def _save(fig, name: str) -> Path:
    _OUT.mkdir(parents=True, exist_ok=True)
    out = _OUT / name
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return out


def _curve_with_band(res, v):
    """a_brake(v) mean and +-1sigma band from the 2x2 covariance (X = [1, v^2])."""
    X = np.column_stack([np.ones_like(v), v ** 2])
    mean = X @ np.array([res.a_b, res.b_b])
    var = np.einsum("ij,jk,ik->i", X, res.covariance, X)
    sd = np.sqrt(np.clip(var, 0.0, None))
    return mean, sd


def plot_arcs(sbr, gp, year):
    samples = sbr.samples
    v = np.array([s.speed for s in samples])
    decel = np.array([-s.a_longitudinal for s in samples])
    arcs = identify_braking_arcs(samples)
    frontier_idx = {i for a in arcs for i in a.sample_indices}
    is_front = np.array([i in frontier_idx for i in range(len(samples))])

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.scatter(v[~is_front], decel[~is_front], s=6, c="0.75", label="non-frontier")
    ax.scatter(v[is_front], decel[is_front], s=10, c="tab:red", label="frontier braking arcs")
    ax.set_xlabel("speed (m/s)"); ax.set_ylabel("deceleration magnitude (m/s$^2$)")
    ax.set_title(f"Braking arcs — {gp} {year} (RBR: {'+'.join(sbr.drivers)})")
    ax.legend()
    return _save(fig, f"braking_view_arcs_{gp}_{year}.png")


def plot_fit(sbr, gp, year):
    res = sbr.result
    vgrid = np.linspace(res.bin_speeds.min(), res.bin_speeds.max(), 200)
    mean, sd = _curve_with_band(res, vgrid)

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.errorbar(res.bin_speeds, res.bin_decel_obs, yerr=np.sqrt(res.bin_var),
                fmt="o", c="tab:blue", label="frontier bins (de-conflated obs)")
    ax.plot(vgrid, mean, c="tab:red", lw=2,
            label=f"a_brake = {res.a_b:.2f} + {res.b_b:.2e}·v²")
    ax.fill_between(vgrid, mean - sd, mean + sd, color="tab:red", alpha=0.2, label="±1σ")
    ax.axhline(sbr.raw_p99_decel, color="0.4", ls="--",
               label=f"raw p99 decel = {sbr.raw_p99_decel:.2f}")
    ax.set_xlabel("speed (m/s)"); ax.set_ylabel("pure braking capability (m/s$^2$)")
    ax.set_title(f"BrakingView fit — {gp} {year}  (b_b {'>' if res.b_b > 0 else '<'} 0)")
    ax.legend()
    return _save(fig, f"braking_view_fit_{gp}_{year}.png")


def plot_prior_posterior(sbr, gp, year):
    res = sbr.result
    vgrid = np.linspace(15.0, 90.0, 200)
    post_mean, post_sd = _curve_with_band(res, vgrid)
    # prior curve from res.prior (cold = flat ~0); draw its mean band for contrast
    Xp = np.column_stack([np.ones_like(vgrid), vgrid ** 2])
    prior_mean = Xp @ res.prior.mu
    prior_var = np.einsum("ij,jk,ik->i", Xp, res.prior.cov, Xp)
    prior_sd = np.sqrt(np.clip(prior_var, 0.0, None))

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.plot(vgrid, prior_mean, c="0.5", lw=1.5, label="prior mean")
    ax.fill_between(vgrid, prior_mean - prior_sd, prior_mean + prior_sd,
                    color="0.5", alpha=0.15, label="prior ±1σ (clipped)")
    ax.plot(vgrid, post_mean, c="tab:red", lw=2, label="posterior mean")
    ax.fill_between(vgrid, post_mean - post_sd, post_mean + post_sd,
                    color="tab:red", alpha=0.25, label="posterior ±1σ")
    ax.set_ylim(0, max(post_mean.max() * 1.4, 1.0))
    ax.set_xlabel("speed (m/s)"); ax.set_ylabel("a_brake(v) (m/s$^2$)")
    ax.set_title(f"Prior → posterior — {gp} {year}")
    ax.legend()
    return _save(fig, f"braking_view_prior_posterior_{gp}_{year}.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2023)
    ap.add_argument("--gp", default="Belgium")
    ap.add_argument("--drivers", nargs="+", default=["VER", "PER"])
    args = ap.parse_args()

    sbr = run_braking_view_on_session(args.year, args.gp, tuple(args.drivers))
    p1 = plot_arcs(sbr, args.gp, args.year)
    p2 = plot_fit(sbr, args.gp, args.year)
    p3 = plot_prior_posterior(sbr, args.gp, args.year)
    r = sbr.result
    print(f"a_b={r.a_b:.3f}  b_b={r.b_b:.3e}  n_bins={r.n_bins}  n_samples={r.n_samples}")
    print(f"raw_p99_decel={sbr.raw_p99_decel:.3f}  drivers={sbr.drivers}")
    print(f"saved: {p1}\n       {p2}\n       {p3}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add scripts/plot_braking_view.py
git commit -m "feat(physics): BrakingView visual confirmation plots — arcs, fit, prior/posterior (#496)"
```

---

## Task 6: Integration run + acceptance on Spa 2023 Q

Run the whole thing on real data and confirm the physics came out right. This is the "strong visual confirmation" gate before we move to Plan 2.

**Files:** none (runs Task 4/5 code).

- [ ] **Step 1: Run the visual confirmation end-to-end**

Run: `py scripts/plot_braking_view.py --year 2023 --gp Belgium --drivers VER PER`
Expected stdout: a line `a_b=… b_b=… n_bins=… n_samples=…`, a `raw_p99_decel=…` line, and three `saved:` paths under `reports/physics/`.

- [ ] **Step 2: Acceptance checks (physics sanity — eyeball + assert)**

Confirm, from stdout and the three PNGs:
- `b_b > 0` — aero braking is **positive** (the headline fix; the raw `fit_braking_frontier` gave it backwards).
- The fitted ceiling near top speed (`a_b + b_b·v_max²`) is in the neighbourhood of `raw_p99_decel` (~5 g ≈ 49 m/s² order), not the over-smoothed ~4.3 g.
- `braking_view_arcs_*.png`: frontier (red) points sit on the upper edge of the decel cloud; gentle braking is greyed out.
- `braking_view_fit_*.png`: the ±1σ band is tight where bins are dense, widens at the extrapolated low-speed intercept.
- `braking_view_prior_posterior_*.png`: posterior is far tighter than the (cold, near-flat) prior — data dominated, as expected at cold start.

If `b_b < 0` or the ceiling is far below `raw_p99_decel`, **stop** — do not patch numbers. Check the regime classification (are `straight_brake` samples actually the hard stops?) and the terrain gradient sign at the Spa braking zones (Les Combes is uphill; `theta > 0` there). Use systematic-debugging.

- [ ] **Step 3: Send the three plots for review**

Surface the three PNGs to the user for the visual sign-off this plan exists to produce.

- [ ] **Step 4: Commit any generated report artifacts (optional)**

```bash
git add reports/physics/braking_view_arcs_Belgium_2023.png reports/physics/braking_view_fit_Belgium_2023.png reports/physics/braking_view_prior_posterior_Belgium_2023.png
git commit -m "chore(physics): Spa 2023 Q BrakingView confirmation plots (#496)"
```

---

## Self-Review (against the spec)

**Spec coverage (this plan = the BrakingView slice of the six-view design):**
- MAP with injectable prior + supporting priors "inflating residual uncertainty" → Task 3 (`GaussianPrior2` prior term + delta-method `var_support`). ✓
- Prior-injectable `(value, σ)`, cold-start vs pinned through one interface → Task 0 (`ParamPrior`/`GaussianPrior2.cold`). ✓
- Both-car/constructor pooling → Task 4 (`drivers=("VER","PER")`, pooled samples). ✓
- Terrain as a first-class input (`z(s)`/`θ(s)` from #497) → Tasks 1 & 3 (`gradient_at_positions`, `g·sinθ` in the balance). ✓
- BrakingView model + supporting priors `CdA[closed]`, `θ_R`, `mass`; primary obs magnitude `d|v|/dt` → Task 3. ✓
- "Residuals/identifiability visible per view" + visual confirmation → Tasks 5–6 (fit band, prior→posterior, `b_b>0` gate). ✓
- Existing `ParameterEstimator`/`braking_fit` untouched (reference) → only `terrain.py` extended, additively. ✓
- **Deferred to later plans (intentional, noted up top):** other five views (Plans 2–6); `SessionEstimator` round loop + `kind=3` Matérn feedback / #498 nesting gate (Plan 7); CdA naming #499; rho-fallback loudness #500; `ForceResidualAnalyzer` #501.

**Placeholder scan:** no "TBD"/"add error handling"/"similar to" — every code/test step carries real content.

**Type consistency:** `ParamPrior(.precision)`, `GaussianPrior2(.precision(), .cold(), .mu, .cov)`, `BrakingView.fit(...)→BrakingViewResult(.a_b,.b_b,.covariance,.bin_speeds,.bin_decel_obs,.bin_var,.prior,.a_brake(),.to_braking_parameters())`, `identify_braking_arcs(...)→list[BrakingArc(.sample_indices,.peak_decel,.mean_speed)]`, `gradient_at_positions(px,py,profile)→ndarray`, `run_braking_view_on_session(...)→SessionBrakingResult(.result,.samples,.theta_per_sample,.rho,.drivers,.raw_p99_decel)` — names used consistently across Tasks 3–6.

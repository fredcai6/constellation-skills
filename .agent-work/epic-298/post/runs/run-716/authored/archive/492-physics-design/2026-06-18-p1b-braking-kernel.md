# P1b — Braking-Peak Recovery via Time Kernel Implementation Plan

> **SUPERSEDED (2026-06-18)** — the kernel was implemented (Tasks 1–4) then
> superseded by the raw-speed braking frontier (workaround) + the physics-aware
> filter rebuild (#496); kernel code removed. Retained as history. See the spec
> header for the rationale.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recover the true braking peak (~5 g) that the smoother flattens (~3.9 g), by fitting a per-event peak-then-decay time kernel to the reliable speed trace and refitting the braking frontier on the de-biased peaks.

**Architecture:** A pluggable kernel registry (normalised peak-early shapes), per-event braking extraction from `straight_brake` samples, a shape-selection fit (amplitude anchored to the event's total Δv; the shape chosen by interior point-wise speed fit), and a frontier refit on the recovered `(v, a_brake)` points. A comparison experiment ranks candidate kernels across cached sessions; the winner's corrected frontier feeds the sim and is judged by P1a's progress-aligned braking-zone Δv.

**Tech Stack:** Python 3.14 (`py`), numpy, the physics data models (`KinematicSample`, `BrakingParameters`), FastF1 offline cache, the P1a sim evaluator, pytest.

## Global Constraints

- Python `py`, never `python`; tests `py -m pytest tests/...`.
- The smoother flattens **accel** but preserves **speed** — fit the kernel to the per-event **speed trace**, never to `a_long`.
- **Amplitude `A` is ANCHORED to the observed total Δv** (`A = v0 − v1`); it is not a free parameter. The kernel **shape** is what the point-wise speed fit selects. The total-Δv integral is thus a guardrail/anchor, not the objective (per the user's "Δv at points; integral is a runaway test").
- Braking decel is a **time kernel**, **not curvature-dependent**, applied **per event**.
- **Generalized kernel + shape this pass; per-driver amplitude/shape tuning is a deferred hook**, defaulting to the generalized value.
- The sim interface is unchanged: P1b outputs a `BrakingParameters` (`a_b`, `b_b`, covariance) refit on recovered peaks; the simulator consumes it as today.
- TDD: failing test first for every pure function; commit per task. Cache-touching paths get a cache-gated smoke (`F1_RUN_CACHE_TESTS=1`).

## File Structure

- `src/physics/braking_kernel.py` — `KERNELS` registry (normalised `g(τ)` shapes); `BrakingEvent` dataclass + `extract_braking_events`; `event_speed_residual`, `recovered_brake_points`, `refit_braking_frontier`.
- `src/physics/braking_kernel_experiment.py` — `compare_kernels(events) -> dict` (pooled ranking) + `pool_events_from_sessions(...)` (cache).
- `scripts/compare_braking_kernels.py` — thin CLI; ranks kernels over cached sessions, prints recovered peak.
- Tests: `tests/unit/physics/test_braking_kernel.py`, `tests/unit/physics/test_braking_kernel_experiment.py`.

---

### Task 1: Kernel registry (normalised peak-early shapes)

**Files:** Create `src/physics/braking_kernel.py` (registry only this task); Test `tests/unit/physics/test_braking_kernel.py`

**Interfaces:**
- Produces: `KERNELS: dict[str, Callable[[np.ndarray], np.ndarray]]` — each maps `τ ∈ [0,1]` to a non-negative shape normalised so `trapz(g, τ) ≈ 1`, peaking in the early half (`argmax < 0.5`). Keys: `"exponential"`, `"gamma"`, `"triangular"`, `"raised_cosine"`.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/physics/test_braking_kernel.py
import numpy as np
import pytest
from src.physics.braking_kernel import KERNELS


@pytest.mark.parametrize("name", ["exponential", "gamma", "triangular", "raised_cosine"])
def test_kernel_normalised_and_peaks_early(name):
    tau = np.linspace(0.0, 1.0, 501)
    g = KERNELS[name](tau)
    assert np.all(g >= 0.0)
    assert np.trapz(g, tau) == pytest.approx(1.0, abs=0.02)   # unit integral
    assert tau[int(np.argmax(g))] < 0.5                       # peaks in early half
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/unit/physics/test_braking_kernel.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the registry**

```python
# src/physics/braking_kernel.py
"""Braking-peak time kernels (Epic 2 P1b, #492).

Each kernel is a normalised deceleration SHAPE g(τ) on τ ∈ [0,1] that peaks
early then decays, with ∫₀¹ g dτ = 1.  Per event the actual decel is
a(t) = (A/T)·g(t/T) where A = v0 − v1 (the reliable total Δv) and T is the
event duration, so the shape — not the amplitude — is what the fit selects.
"""
from __future__ import annotations

from typing import Callable, Dict

import numpy as np


def _normalise(tau: np.ndarray, g: np.ndarray) -> np.ndarray:
    g = np.clip(g, 0.0, None)
    area = np.trapz(g, tau)
    return g / area if area > 0 else g


def _exponential(tau: np.ndarray, k: float = 4.0) -> np.ndarray:
    return _normalise(tau, np.exp(-k * tau))            # peaks at τ=0, decays


def _gamma(tau: np.ndarray, a: float = 2.0, b: float = 8.0) -> np.ndarray:
    return _normalise(tau, np.power(tau, a - 1) * np.exp(-b * tau))  # peak at (a-1)/b


def _triangular(tau: np.ndarray, peak: float = 0.2) -> np.ndarray:
    g = np.where(tau <= peak, tau / peak, np.clip((1 - tau) / (1 - peak), 0, None))
    return _normalise(tau, g)


def _raised_cosine(tau: np.ndarray, peak: float = 0.2) -> np.ndarray:
    # rise as half-cosine to `peak`, decay as half-cosine to 1
    rise = 0.5 * (1 - np.cos(np.pi * np.clip(tau / peak, 0, 1)))
    fall = 0.5 * (1 + np.cos(np.pi * np.clip((tau - peak) / (1 - peak), 0, 1)))
    return _normalise(tau, np.where(tau <= peak, rise, fall))


KERNELS: Dict[str, Callable[[np.ndarray], np.ndarray]] = {
    "exponential": _exponential,
    "gamma": _gamma,
    "triangular": _triangular,
    "raised_cosine": _raised_cosine,
}
```

- [ ] **Step 4: Run test to verify it passes** — `py -m pytest tests/unit/physics/test_braking_kernel.py -v` → PASS (4).

- [ ] **Step 5: Commit**

```bash
git add src/physics/braking_kernel.py tests/unit/physics/test_braking_kernel.py
git commit -m "feat(physics): braking-peak kernel registry (#492 P1b)"
```

---

### Task 2: Braking-event extraction

**Files:** Modify `src/physics/braking_kernel.py`; Test `tests/unit/physics/test_braking_kernel.py`

**Interfaces:**
- Consumes: `KinematicSample` (has `timestamp_ms`, `speed`, `regime`).
- Produces: `BrakingEvent` (frozen: `t` ndarray s from event start, `v` ndarray m/s, `v0`, `v1`, `T`); `extract_braking_events(samples, *, min_pts=5, min_dv_ms=5.0) -> list[BrakingEvent]` — contiguous `straight_brake` runs with ≥ `min_pts` samples and `v0 − v1 ≥ min_dv_ms` (drops light braking; keeps genuine stops).

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/physics/test_braking_kernel.py (add)
from src.physics.braking_kernel import extract_braking_events, BrakingEvent
from src.physics.physics_data_models import KinematicSample, ControlState


def _sample(ts_ms, speed, regime):
    return KinematicSample(
        timestamp_ms=ts_ms, position=np.zeros(3), velocity=np.array([speed, 0, 0]),
        acceleration=np.zeros(3), covariance=np.zeros((9, 9)), speed=speed,
        a_longitudinal=-10.0 if regime == "straight_brake" else 0.0, a_lateral=0.0,
        curvature=0.0,
        control=ControlState(timestamp_ms=ts_ms, throttle_confidence=1.0,
                             throttle_value=0.0, brake_probability=1.0),
        regime=regime,
    )


def test_extract_braking_events_groups_contiguous_brake_runs():
    # one strong braking run (90→60 m/s over 6 pts) bracketed by non-brake samples
    samples = [_sample(0, 95, "straight_throttle")]
    for i, v in enumerate([90, 84, 78, 72, 66, 60]):
        samples.append(_sample(100 * (i + 1), v, "straight_brake"))
    samples.append(_sample(700, 60, "corner"))
    events = extract_braking_events(samples, min_pts=5, min_dv_ms=5.0)
    assert len(events) == 1
    ev = events[0]
    assert ev.v0 == pytest.approx(90.0)
    assert ev.v1 == pytest.approx(60.0)
    assert ev.t[0] == pytest.approx(0.0)
    assert ev.T == pytest.approx(0.5)  # 0..500 ms


def test_extract_braking_events_drops_light_and_short_runs():
    samples = [_sample(100 * i, 80 - i, "straight_brake") for i in range(3)]  # 3 pts, Δv=2
    assert extract_braking_events(samples, min_pts=5, min_dv_ms=5.0) == []
```

- [ ] **Step 2: Run** → FAIL (names missing).

- [ ] **Step 3: Implement**

```python
# src/physics/braking_kernel.py (add)
from dataclasses import dataclass


@dataclass(frozen=True)
class BrakingEvent:
    t: np.ndarray      # seconds from event start
    v: np.ndarray      # observed speed (m/s)
    v0: float
    v1: float
    T: float


def extract_braking_events(samples, *, min_pts: int = 5, min_dv_ms: float = 5.0):
    events = []
    run: list = []

    def _flush(run):
        if len(run) < min_pts:
            return
        ts = np.array([s.timestamp_ms for s in run], dtype=float) / 1000.0
        v = np.array([s.speed for s in run], dtype=float)
        t = ts - ts[0]
        v0, v1 = float(v[0]), float(v[-1])
        if (v0 - v1) < min_dv_ms or t[-1] <= 0:
            return
        events.append(BrakingEvent(t=t, v=v, v0=v0, v1=v1, T=float(t[-1])))

    for s in samples:
        if s.regime == "straight_brake":
            run.append(s)
        else:
            _flush(run)
            run = []
    _flush(run)
    return events
```

- [ ] **Step 4: Run** → PASS (2 new).
- [ ] **Step 5: Commit** — `git commit -m "feat(physics): braking-event extraction from brake-regime runs (#492 P1b)"`

---

### Task 3: Shape-selection fit + frontier refit

**Files:** Modify `src/physics/braking_kernel.py`; Test `tests/unit/physics/test_braking_kernel.py`

**Interfaces:**
- Produces:
  - `event_speed_residual(event, g) -> float` — RMS of `v_pred(t) − v_obs(t)` where `v_pred(t) = v0 − A·G(t/T)`, `A = v0 − v1`, `G` = numeric cumulative integral of `g` normalised to `G(1)=1`.
  - `recovered_brake_points(event, g) -> tuple[np.ndarray, np.ndarray]` — `(v(t), a(t))` with `a(t) = (A/T)·g(t/T)` (m/s²), the de-biased decel-vs-speed samples for this event.
  - `refit_braking_frontier(events, g, *, prior_cov=None) -> BrakingParameters | None` — pool all events' recovered `(v, a)`, OLS-fit `a = a_b + b_b·v²` (clamp `a_b ≥ 0`), return `BrakingParameters` with a 2×2 covariance (honest `s²(XᵀX)⁻¹`).

- [ ] **Step 1: Write the failing test** (synthetic event built FROM a known kernel must (a) be best-fit by that kernel, (b) recover its peak)

```python
# tests/unit/physics/test_braking_kernel.py (add)
from src.physics.braking_kernel import (
    event_speed_residual, recovered_brake_points, refit_braking_frontier, KERNELS,
)
from src.physics.physics_data_models import BrakingParameters


def _event_from_kernel(name, v0=90.0, v1=55.0, T=1.2, n=25):
    g = KERNELS[name]
    tau = np.linspace(0, 1, 4001)
    G = np.concatenate([[0.0], np.cumsum((g(tau)[1:] + g(tau)[:-1]) / 2 * np.diff(tau))])
    G = G / G[-1]
    t = np.linspace(0, T, n)
    A = v0 - v1
    v = v0 - A * np.interp(t / T, tau, G)
    from src.physics.braking_kernel import BrakingEvent
    return BrakingEvent(t=t, v=v, v0=v0, v1=v1, T=T)


def test_true_kernel_minimises_residual():
    ev = _event_from_kernel("gamma")
    res = {name: event_speed_residual(ev, KERNELS[name]) for name in KERNELS}
    assert min(res, key=res.get) == "gamma"
    assert res["gamma"] < 0.5  # m/s RMS — near-exact for the generating kernel


def test_recovered_peak_exceeds_mean_decel():
    ev = _event_from_kernel("gamma", v0=90, v1=55, T=1.2)
    v, a = recovered_brake_points(ev, KERNELS["gamma"])
    mean_decel = (ev.v0 - ev.v1) / ev.T            # ~29 m/s / 1.2 s ≈ 24 m/s²
    assert a.max() > 1.5 * mean_decel              # peaked kernel >> mean


def test_refit_frontier_returns_braking_parameters():
    events = [_event_from_kernel("gamma", v0=90 - 3*i, v1=55 - 2*i) for i in range(6)]
    bp = refit_braking_frontier(events, KERNELS["gamma"])
    assert isinstance(bp, BrakingParameters)
    assert bp.a_b >= 0.0
    assert bp.covariance.shape == (2, 2)
```

- [ ] **Step 2: Run** → FAIL.

- [ ] **Step 3: Implement**

```python
# src/physics/braking_kernel.py (add)
from src.physics.physics_data_models import BrakingParameters

_TAU = np.linspace(0.0, 1.0, 2001)


def _cdf(g) -> np.ndarray:
    gv = g(_TAU)
    G = np.concatenate([[0.0], np.cumsum((gv[1:] + gv[:-1]) / 2 * np.diff(_TAU))])
    return G / G[-1] if G[-1] > 0 else G


def event_speed_residual(event, g) -> float:
    A = event.v0 - event.v1
    G = _cdf(g)
    v_pred = event.v0 - A * np.interp(event.t / event.T, _TAU, G)
    return float(np.sqrt(np.mean((v_pred - event.v) ** 2)))


def recovered_brake_points(event, g):
    A = event.v0 - event.v1
    G = _cdf(g)
    u = event.t / event.T
    v = event.v0 - A * np.interp(u, _TAU, G)        # speed along the event
    a = (A / event.T) * g(u)                          # de-biased decel (m/s²)
    return v, a


def refit_braking_frontier(events, g, *, prior_cov=None):
    vs, as_ = [], []
    for ev in events:
        v, a = recovered_brake_points(ev, g)
        vs.append(v); as_.append(a)
    if not vs:
        return None
    v = np.concatenate(vs); a = np.concatenate(as_)
    X = np.column_stack([np.ones_like(v), v ** 2])
    coef, *_ = np.linalg.lstsq(X, a, rcond=None)
    a_b = max(float(coef[0]), 0.0)
    b_b = float(coef[1])
    resid = a - X @ coef
    dof = max(len(a) - 2, 1)
    cov = (float(resid @ resid) / dof) * np.linalg.pinv(X.T @ X)
    return BrakingParameters(a_b=a_b, b_b=b_b, covariance=cov)
```

- [ ] **Step 4: Run** → PASS (3 new).
- [ ] **Step 5: Commit** — `git commit -m "feat(physics): kernel shape-fit + braking frontier refit on recovered peaks (#492 P1b)"`

---

### Task 4: Kernel-comparison experiment

**Files:** Create `src/physics/braking_kernel_experiment.py`, `scripts/compare_braking_kernels.py`; Test `tests/unit/physics/test_braking_kernel_experiment.py`

**Interfaces:**
- Produces: `compare_kernels(events) -> dict` — `{kernel_name: {"median_residual": float, "recovered_peak_g": float, "b_b": float, "n_events": int}}`, ranked; `pool_events_from_sessions(db_path, cache, year, limit=None) -> list[BrakingEvent]` (re-fit sessions via `session_fit`/`segment_classifier`, pool `straight_brake` events).

- [ ] **Step 1: Write the failing test (pure `compare_kernels`)**

```python
# tests/unit/physics/test_braking_kernel_experiment.py
import numpy as np
import pytest
from src.physics import braking_kernel_experiment as bke
from src.physics.braking_kernel import KERNELS
from tests.unit.physics.test_braking_kernel import _event_from_kernel


def test_compare_kernels_ranks_generating_kernel_first():
    events = [_event_from_kernel("gamma", v0=90 - 2*i, v1=55 - i) for i in range(8)]
    out = bke.compare_kernels(events)
    best = min(out, key=lambda k: out[k]["median_residual"])
    assert best == "gamma"
    assert out["gamma"]["recovered_peak_g"] > 0
    assert out["gamma"]["n_events"] == 8
```

- [ ] **Step 2: Run** → FAIL.

- [ ] **Step 3: Implement `compare_kernels` (pure) + `pool_events_from_sessions` (cache)**

```python
# src/physics/braking_kernel_experiment.py
"""Compare braking kernels over pooled events (Epic 2 P1b, #492)."""
from __future__ import annotations

import numpy as np

from src.physics.braking_kernel import (
    KERNELS, event_speed_residual, recovered_brake_points, refit_braking_frontier,
)

G_MS2 = 9.81


def compare_kernels(events) -> dict:
    out = {}
    for name, g in KERNELS.items():
        if not events:
            out[name] = {"median_residual": float("inf"), "recovered_peak_g": 0.0,
                         "b_b": 0.0, "n_events": 0}
            continue
        res = [event_speed_residual(ev, g) for ev in events]
        peaks = [recovered_brake_points(ev, g)[1].max() for ev in events]
        bp = refit_braking_frontier(events, g)
        out[name] = {
            "median_residual": float(np.median(res)),
            "recovered_peak_g": float(np.median(peaks) / G_MS2),
            "b_b": float(bp.b_b) if bp else 0.0,
            "n_events": len(events),
        }
    return dict(sorted(out.items(), key=lambda kv: kv[1]["median_residual"]))
```

`pool_events_from_sessions`: for each `ok` store row, `load_quali_session` → for the driver's flying laps run the smoother chain to `processed_telemetry` (reuse `session_fit`'s internals) → `SegmentClassifier` → `extract_braking_events`; pool. Cover with a cache-gated smoke (assert a non-empty event pool and that `compare_kernels` returns a finite best residual on real Monaco/Spain braking).

- [ ] **Step 4: Run pure test** → PASS.
- [ ] **Step 5: Cache-gated smoke** (real events; assert pool non-empty + finite ranking).
- [ ] **Step 6: Thin CLI** `scripts/compare_braking_kernels.py` → prints the ranking table + the winning kernel's recovered peak (g) and `b_b`.
- [ ] **Step 7: Commit** — `git commit -m "feat(physics): braking-kernel comparison experiment (#492 P1b)"`

---

### Task 5: Wire the corrected frontier into the sim + re-evaluate (verification)

**Files:** none new (a verification + small wiring step).

- [ ] **Step 1: Run the experiment** — `F1_RUN_CACHE_TESTS=1 py scripts/compare_braking_kernels.py --year 2023 --limit 30`. Read the ranking: which kernel wins, what recovered peak (target ~5 g, vs the ~3.9 g baseline), and does `b_b ≥ 0` (downforce-assisted, "peak early")?
- [ ] **Step 2: Apply the winning kernel's refit frontier in the per-session fit** (feed `refit_braking_frontier` output into the `BrakingParameters` the sim uses, behind a config/flag so the old path stays available), then re-run `scripts/run_sim_evaluator.py --year 2023 --limit 20`.
- [ ] **Step 3: Compare braking-zone Δv before/after** — does the sim stop under-calling decel into corners (Δv ≥ 0 through braking zones, now progress-registered)? Summarise the recovered peak, winning kernel, and the Δv change in `reports/physics/P1b_braking_kernel_findings.md`; commit it.

---

## Self-Review

**Spec coverage** (`2026-06-18-p1b-braking-peak-kernel-design.md`): time kernel not curvature-dependent (Task 1 shapes in τ) ✓; per-event (Task 2) ✓; fit to speed trace with A anchored to Δv, shape selected by point-wise residual (Task 3 `event_speed_residual`) ✓; integral as guardrail (A = v0−v1 anchor) ✓; try several kernels (Task 1 registry + Task 4 compare) ✓; recovered peak → frontier refit, sim interface unchanged (Task 3 `refit_braking_frontier` → `BrakingParameters`) ✓; evaluate via P1a diagnostic (Task 5) ✓; generalized now, per-driver deferred (no per-driver code; hook implicit in amplitude=Δv per event) ✓.

**Placeholder scan:** `pool_events_from_sessions` body is described (reuses `session_fit` internals + `SegmentClassifier`) rather than fully coded, because it depends on reading those internals during implementation; it is cache-gated-smoke-covered and its inputs/outputs are specified. All pure functions have complete code + tests.

**Type consistency:** `KERNELS[name]: Callable[[ndarray], ndarray]` used identically in Tasks 1/3/4; `BrakingEvent` fields (`t,v,v0,v1,T`) consistent across Tasks 2/3; `refit_braking_frontier → BrakingParameters` matches the sim's existing type.

**Known follow-ups (out of P1b):** per-driver amplitude/shape tuning; the ribbon-optimal-line ceiling (ii, skipped); recovering #495-errored sessions to deepen the event pool.

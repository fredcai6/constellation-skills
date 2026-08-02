# P1a — Sim as Two-Sided Evaluator (Gsat guard + DRS mask + diagnostic) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the ideal-lap sim a runnable, DRS-aware, two-sided evaluator: no aphysical corner runaways, real DRS-open top speed, and a diagnostic that reports per-point Δv-vs-position over the P0 fit store.

**Architecture:** Three pieces. (B) a per-car Gsat fallback ceiling in `PhysicsSimulator._compute_speed_caps` so every corner is finite even when no tyre ceiling was fit. (A) a DRS-zone mask on the ribbon (`drs_open(s)`), pooled from the FastF1 DRS channel across laps, which the sim already consumes. (D) a `sim_evaluator` module: pure diagnostic metrics + a runner that rebuilds each car-session's geometry (ribbon) and params (P0 store), simulates the ideal lap, and reports Δv-vs-position / gap / runaway flags. Braking-peak correction is a separate follow-on plan (P1b) that this diagnostic will evaluate.

**Tech Stack:** Python 3.14 (`py`), numpy, pandas, FastF1 (offline cache), the P0 `FitStore`, pytest.

## Global Constraints

- Python is invoked as `py`, never `python`. Tests run via `py -m pytest tests/...`.
- The ideal lap is a CEILING, not a regression-to-quali target. A *large* ideal-vs-best gap (~10%) is healthy; a *couple-percent* gap is the suspicious under-call signal. Per-point Δv-vs-position is the primary read; the lap-time gap is a summary.
- Runaway is a separate physics-implausibility check (uncapped/over-speed corners, impossible speeds), NOT inferred from a large gap.
- Gsat fallback ceiling is per-car, derived from the car's own grip, **clamped by an era/population max**, with a hook so P2 can later inject a pooled per-car ceiling. It only applies when `lateral.ceiling is None` (a real fitted ceiling always wins).
- DRS mask is telemetry-pooled (no curated per-season zone file) so it is valid across all seasons; a DRS-disabled session simply yields no zones.
- Reuse existing patterns: the sim already reads a `drs_open` column via `_extract_track_profile`; the ribbon already returns `{distance_m, curvature}`; do not restructure them, extend them.
- TDD: failing test first for every pure function; commit per task. Integration paths that need the FastF1 cache get a cache-gated smoke test (env `F1_RUN_CACHE_TESTS=1`), mirroring P0's `session_fit` smoke.

## File Structure

- `src/physics/physics_config.py` — add Gsat fields (`gsat_population_max_g`, `gsat_reference_speed_ms`, `gsat_headroom`).
- `src/physics/physics_simulator.py` — add `_gsat_ceiling(parameters, air_density, override)`; use it as the fallback in `_compute_speed_caps`; thread an optional `gsat_ceiling_override` through `simulate_lap`/`_compute_speed_caps`.
- `src/physics/ribbon.py` — add pure `drs_zone_mask(laps_drs, n_grid, threshold)`; extend `build_session_ribbon` to pool the DRS channel and add a `drs_open` array to the returned dict.
- `src/physics/sim_evaluator.py` (new) — pure metrics (`delta_v_profile`, `lap_gap_pct`, `runaway_flags`) + `evaluate_session(...)` + `evaluate_store(...)`.
- `scripts/run_sim_evaluator.py` (new) — thin CLI over `evaluate_store`.
- Tests: `tests/unit/physics/test_physics_simulator.py` (extend), `tests/unit/physics/test_ribbon.py` (extend), `tests/unit/physics/test_sim_evaluator.py` (new).

---

### Task 1: Per-car Gsat runaway guard (B)

**Files:**
- Modify: `src/physics/physics_config.py` (add 3 fields)
- Modify: `src/physics/physics_simulator.py` (`_gsat_ceiling`, `_compute_speed_caps`, `simulate_lap`)
- Test: `tests/unit/physics/test_physics_simulator.py`

**Interfaces:**
- Consumes: `PhysicsParameterSet.lateral` (`A0`, `A2`, `g_track`, `ceiling`), `config.reference_density_kg_m3`.
- Produces: `PhysicsSimulator._gsat_ceiling(parameters, air_density, override=None) -> float` (m/s²); `simulate_lap(track_profile, parameters, sample=True, gsat_ceiling_override=None)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/physics/test_physics_simulator.py (add)
import numpy as np
import pandas as pd
from src.physics.physics_simulator import PhysicsSimulator
from src.physics.physics_config import PhysicsEstimatorConfig
from src.physics.physics_data_models import (
    PhysicsParameterSet, LongitudinalParameters, LateralParameters,
)


def _params_no_ceiling(A2):
    lon = LongitudinalParameters(theta_D=8e-4, theta_R=0.02, theta_D_std=1e-5,
                                 theta_R_std=1e-4, theta_P_times=np.array([0.0, 1.0]),
                                 theta_P_values=np.array([300.0, 300.0]))
    lat = LateralParameters(A0=30.0, A2=A2, k_tire=0.0, g_track=1.0,
                            covariance=None, ceiling=None)  # NO ceiling
    return PhysicsParameterSet(driver_id="X", session_id=0, longitudinal=lon,
                               lateral=lat, n_samples_used=100, fit_quality_metrics={},
                               fit_air_density=1.2)


def test_high_aero_no_ceiling_corner_is_finite():
    # A high A2 with no ceiling makes denom = κ - A2·ρ ≤ 0 on a fast corner,
    # which previously left the speed cap at +inf (runaway). The Gsat fallback
    # must make it finite.
    cfg = PhysicsEstimatorConfig.from_config()
    sim = PhysicsSimulator(cfg)
    # fast corner: small curvature; A2·ρ chosen so denom ≤ 0
    curvatures = np.array([0.0, 1e-3, 0.0])
    caps = sim._compute_speed_caps(curvatures, _params_no_ceiling(A2=2e-3), air_density=1.2)
    assert np.isfinite(caps[1])


def test_gsat_ceiling_clamped_by_population_max():
    cfg = PhysicsEstimatorConfig.from_config()
    sim = PhysicsSimulator(cfg)
    # Enormous A2 would imply absurd lateral g at v_ref; clamp must cap it.
    g = sim._gsat_ceiling(_params_no_ceiling(A2=1.0), air_density=1.2)
    assert g <= cfg.gsat_population_max_g * 9.81 + 1e-9


def test_gsat_override_hook_wins():
    cfg = PhysicsEstimatorConfig.from_config()
    sim = PhysicsSimulator(cfg)
    g = sim._gsat_ceiling(_params_no_ceiling(A2=2e-3), air_density=1.2, override=42.0)
    assert g == 42.0


def test_fitted_ceiling_takes_precedence_over_gsat():
    cfg = PhysicsEstimatorConfig.from_config()
    sim = PhysicsSimulator(cfg)
    p = _params_no_ceiling(A2=2e-3)
    p.lateral.ceiling = 28.0  # a real fitted ceiling
    curvatures = np.array([0.0, 1e-3, 0.0])
    caps = sim._compute_speed_caps(curvatures, p, air_density=1.2)
    # cap = sqrt(ceiling/κ) with the FITTED ceiling, not the gsat fallback
    assert caps[1] == np.sqrt(28.0 / 1e-3)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/unit/physics/test_physics_simulator.py -k "gsat or no_ceiling or fitted_ceiling" -v`
Expected: FAIL — `gsat_population_max_g` not on config / `_gsat_ceiling` missing / `caps[1]` is `inf`.

- [ ] **Step 3a: Add config fields**

```python
# src/physics/physics_config.py — add near the simulator fields (after simulator_start_speed_ms)
    gsat_population_max_g: float = 6.0
    """Era/population absolute lateral-g clamp for the Gsat runaway-guard
    fallback ceiling (used only when no tyre ceiling was fitted)."""

    gsat_reference_speed_ms: float = 70.0
    """High-speed reference (m/s) at which the car's own lateral capability is
    read to seed the per-car Gsat fallback ceiling."""

    gsat_headroom: float = 1.05
    """Multiplier on the car-derived Gsat so the guard ceiling sits just above
    demonstrated capability (a guard, not a clip)."""
```

- [ ] **Step 3b: Add `_gsat_ceiling` and wire it into the speed caps**

```python
# src/physics/physics_simulator.py

def _gsat_ceiling(self, parameters, air_density, override=None) -> float:
    """Per-car fallback lateral-accel ceiling (m/s²) for the runaway guard.

    Used ONLY when no tyre ceiling was fitted. Seeded from the car's own
    lateral capability at a high reference speed, lifted by a small headroom,
    then clamped by the era/population max. ``override`` (e.g. a pooled P2
    posterior) wins when supplied.
    """
    if override is not None:
        return float(override)
    lat = parameters.lateral
    v_ref = self.config.gsat_reference_speed_ms
    car_lat = lat.A0 * lat.g_track + lat.A2 * air_density * v_ref * v_ref
    guarded = car_lat * self.config.gsat_headroom
    pop_max = self.config.gsat_population_max_g * 9.81
    return float(min(guarded, pop_max))
```

Then in `_compute_speed_caps`, replace the `ceil_cap` line so a missing ceiling uses the Gsat fallback instead of `inf`. Change the signature to accept the override and compute a fallback once:

```python
def _compute_speed_caps(self, curvatures, parameters, air_density, gsat_ceiling_override=None):
    caps = np.full_like(curvatures, np.inf, dtype=float)
    A0 = parameters.lateral.A0 * parameters.lateral.g_track
    A2 = parameters.lateral.A2
    ceiling = parameters.lateral.ceiling
    fallback = self._gsat_ceiling(parameters, air_density, gsat_ceiling_override)
    eff_ceiling = ceiling if ceiling is not None else fallback   # always finite
    for i, curvature in enumerate(curvatures):
        curvature = abs(float(curvature))
        if curvature < self.config.simulator_curvature_threshold:
            continue
        ceil_cap = np.sqrt(eff_ceiling / curvature)
        denom = curvature - A2 * air_density
        if denom <= 0.0:
            caps[i] = float(ceil_cap)
            continue
        # ... existing A0/A2 branch unchanged, but final cap is min(existing, ceil_cap)
```

Keep the existing A0/A2 cornering-speed computation in the `denom > 0` branch; just take `min(grip_cap, ceil_cap)` as the per-point cap so the guard also bounds the aero-rising branch. (Read the current lines 481-489 and apply `min`.)

- [ ] **Step 3c: Thread the override through `simulate_lap`**

```python
# simulate_lap signature: add gsat_ceiling_override=None
def simulate_lap(self, track_profile, parameters, sample=True, gsat_ceiling_override=None):
    ...
    speed_caps = self._compute_speed_caps(curvatures, parameters, air_density, gsat_ceiling_override)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `py -m pytest tests/unit/physics/test_physics_simulator.py -v`
Expected: PASS (new tests green; existing simulator tests still green — the guard only changes the previously-`inf` path and adds a `min`).

- [ ] **Step 5: Commit**

```bash
git add src/physics/physics_config.py src/physics/physics_simulator.py tests/unit/physics/test_physics_simulator.py
git commit -m "feat(physics): per-car Gsat runaway guard for uncapped corners (#492 P1)"
```

---

### Task 2: DRS-zone mask on the ribbon (A)

**Files:**
- Modify: `src/physics/ribbon.py` (`drs_zone_mask`, extend `build_session_ribbon`)
- Test: `tests/unit/physics/test_ribbon.py`

**Interfaces:**
- Consumes: the FastF1 session DRS channel (per driver, `car_data[num]["DRS"]`), the ribbon's progress grid.
- Produces: `drs_zone_mask(laps_drs, n_grid, threshold=0.5) -> np.ndarray[bool]` (pure); `build_session_ribbon(...) -> {"distance_m", "curvature", "drs_open"}`.

DRS decode note: FastF1 `DRS` values 10/12/14 mean DRS open/active; 0/1/8 mean closed/available. Treat `drs_value in (10, 12, 14)` as open (mirror the existing decode used in the estimator; confirm against `control_alignment.py`).

- [ ] **Step 1: Write the failing test (pure mask)**

```python
# tests/unit/physics/test_ribbon.py (add)
import numpy as np
from src.physics.ribbon import drs_zone_mask


def test_drs_zone_mask_marks_consistently_open_segment():
    # 3 laps, each a boolean open-state over its own progress grid; the back
    # third is open on all laps -> a zone; the front is never open.
    n = 30
    laps = []
    for _ in range(3):
        d = np.zeros(n, dtype=bool)
        d[20:] = True
        laps.append(d)
    mask = drs_zone_mask(laps, n_grid=30, threshold=0.5)
    assert mask[25] == True   # noqa: E712  (open across all laps)
    assert mask[5] == False   # noqa: E712  (never open)


def test_drs_zone_mask_threshold_excludes_one_off_opens():
    n = 30
    laps = [np.zeros(n, dtype=bool) for _ in range(3)]
    laps[0][10:15] = True  # only one lap opened here -> below threshold
    mask = drs_zone_mask(laps, n_grid=30, threshold=0.5)
    assert mask[12] == False  # noqa: E712


def test_drs_zone_mask_no_open_returns_all_false():
    laps = [np.zeros(20, dtype=bool) for _ in range(4)]
    mask = drs_zone_mask(laps, n_grid=20, threshold=0.5)
    assert not mask.any()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/unit/physics/test_ribbon.py -k drs -v`
Expected: FAIL — `cannot import name 'drs_zone_mask'`.

- [ ] **Step 3: Implement `drs_zone_mask` and extend the session ribbon**

```python
# src/physics/ribbon.py (add)

def drs_zone_mask(laps_drs, n_grid: int, threshold: float = 0.5) -> np.ndarray:
    """Pool per-lap DRS-open states onto the ribbon grid → a zone mask.

    Each element of ``laps_drs`` is a 1-D boolean array of DRS-open state
    sampled along that lap's own progress (any length). Each is resampled onto
    ``n_grid`` uniform progress points (nearest-sample) and averaged across
    laps; a grid point is a DRS *zone* where the open fraction ≥ ``threshold``.
    Telemetry-pooled: a segment is a zone only where DRS is open on most laps,
    so it self-adapts to each season and to DRS-disabled sessions (→ all False).
    """
    if not laps_drs:
        return np.zeros(n_grid, dtype=bool)
    u_grid = np.linspace(0.0, 1.0, n_grid)
    acc = np.zeros(n_grid, dtype=float)
    for d in laps_drs:
        d = np.asarray(d, dtype=bool)
        if d.size == 0:
            continue
        u_lap = np.linspace(0.0, 1.0, d.size)
        idx = np.clip(np.searchsorted(u_lap, u_grid), 0, d.size - 1)
        acc += d[idx].astype(float)
    frac = acc / len(laps_drs)
    return frac >= threshold
```

Then in `build_session_ribbon`, while iterating each (driver, lap), also collect the lap's DRS-open boolean (from `session.car_data[drv_num]` clipped to the lap window, decoded `in (10,12,14)`), append to a `laps_drs` list, and add `drs_open=drs_zone_mask(laps_drs, n_grid)` to the returned dict. Keep `build_ribbon` (the agnostic core) unchanged — DRS pooling lives only in the session layer.

```python
# inside build_session_ribbon, return:
    ribbon = build_ribbon(laps_xy, n_grid=n_grid, smooth_window=smooth_window, min_laps=min_laps)
    ribbon["drs_open"] = drs_zone_mask(laps_drs, n_grid=n_grid)
    return ribbon
```

(Read the existing loop ~lines 308-336 and add a DRS collection alongside the `laps_xy.append(...)`; decode helper: `open_state = np.isin(drs_raw, (10, 12, 14))`.)

- [ ] **Step 4: Run pure tests to verify they pass**

Run: `py -m pytest tests/unit/physics/test_ribbon.py -k drs -v`
Expected: PASS.

- [ ] **Step 5: Add a cache-gated smoke test (real DRS zones)**

```python
# tests/unit/physics/test_ribbon.py (add)
import os
import pytest

@pytest.mark.skipif(os.environ.get("F1_RUN_CACHE_TESTS") != "1",
                    reason="offline FastF1 cache smoke (set F1_RUN_CACHE_TESTS=1)")
def test_build_session_ribbon_has_drs_zones_on_monza():
    import fastf1
    fastf1.Cache.enable_cache("outputs/cache")
    try:
        fastf1.Cache.offline_mode(True)
    except AttributeError:
        pass
    s = fastf1.get_session(2023, "Italy", "Q")
    s.load(telemetry=True, laps=True, weather=False)
    from src.physics.ribbon import build_session_ribbon
    rib = build_session_ribbon(s, ["VER", "LEC", "SAI"])
    assert "drs_open" in rib
    assert rib["drs_open"].any()   # Monza has long DRS straights
    frac = rib["drs_open"].mean()
    assert 0.05 < frac < 0.6       # plausible DRS coverage fraction
```

- [ ] **Step 6: Run the smoke (cache present)**

Run: `F1_RUN_CACHE_TESTS=1 py -m pytest tests/unit/physics/test_ribbon.py::test_build_session_ribbon_has_drs_zones_on_monza -v`
Expected: PASS (or SKIP if 2023 Italy Q not cached). If it fails on the DRS-decode, verify the open codes against `src/physics/control_alignment.py` and fix the decode, not the test.

- [ ] **Step 7: Commit**

```bash
git add src/physics/ribbon.py tests/unit/physics/test_ribbon.py
git commit -m "feat(physics): pooled DRS-zone mask on the session ribbon (#492 P1)"
```

---

### Task 3: Two-sided diagnostic (D)

**Files:**
- Create: `src/physics/sim_evaluator.py`
- Create: `scripts/run_sim_evaluator.py`
- Test: `tests/unit/physics/test_sim_evaluator.py`

**Interfaces:**
- Consumes: `FitStore.load_fits` (P0), `build_session_ribbon` + `drs_open` (Task 2), `PhysicsSimulator.simulate_lap` (Task 1), `session_fit.load_quali_session`, the reconstructed `PhysicsParameterSet`.
- Produces:
  - `delta_v_profile(distance, v_sim, v_real) -> np.ndarray` (m/s, sim−real interpolated onto `distance`).
  - `lap_gap_pct(sim_lap_s, real_lap_s) -> float` (positive = ideal faster).
  - `runaway_flags(v_sim, speed_caps_hit, *, max_plausible_ms) -> dict` (impossible-speed / cap-saturation booleans).
  - `evaluate_session(...) -> dict` (one car-session row of metrics).
  - `evaluate_store(db_path, cache, year, limit=None) -> pandas.DataFrame`.

- [ ] **Step 1: Write the failing test (pure metrics)**

```python
# tests/unit/physics/test_sim_evaluator.py
import numpy as np
import pytest
from src.physics import sim_evaluator as se


def test_delta_v_profile_interpolates_and_subtracts():
    dist = np.array([0.0, 100.0, 200.0])
    v_sim = np.array([50.0, 60.0, 70.0])
    v_real = np.array([48.0, 60.0, 66.0])
    dv = se.delta_v_profile(dist, v_sim, v_real)
    assert dv.tolist() == [2.0, 0.0, 4.0]


def test_lap_gap_pct_positive_when_ideal_faster():
    assert se.lap_gap_pct(81.0, 90.0) == pytest.approx(10.0)


def test_runaway_flags_detect_impossible_speed():
    v = np.array([50.0, 400.0, 60.0])  # 400 m/s = 1440 km/h, impossible
    out = se.runaway_flags(v, speed_caps_hit=0.0, max_plausible_ms=100.0)
    assert out["impossible_speed"] is True


def test_runaway_flags_clean_profile():
    v = np.array([50.0, 80.0, 60.0])
    out = se.runaway_flags(v, speed_caps_hit=0.1, max_plausible_ms=100.0)
    assert out["impossible_speed"] is False


def test_lap_gap_small_is_under_call_suspect():
    # a couple-percent gap is suspicious (under-call); helper exposes the flag
    assert se.is_under_call_suspect(se.lap_gap_pct(88.5, 90.0)) is True   # ~1.7%
    assert se.is_under_call_suspect(se.lap_gap_pct(81.0, 90.0)) is False  # ~10%
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/unit/physics/test_sim_evaluator.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the pure metrics**

```python
# src/physics/sim_evaluator.py
"""Two-sided ideal-lap diagnostic over the P0 fit store (Epic 2 P1, #492).

The ideal lap is a CEILING. We read (1) per-point Δv-vs-position (the primary
signal: where the sim under/over-shoots the real best lap), (2) the lap-time
gap as a summary (a couple-% gap = under-call suspect; ~10% is healthy), and
(3) runaway flags (impossible speeds / corner-cap saturation).
"""
from __future__ import annotations

import numpy as np

UNDER_CALL_GAP_PCT = 3.0       # gap below this % flags an under-call suspect
MAX_PLAUSIBLE_SPEED_MS = 110.0  # ~400 km/h; above this is aphysical


def delta_v_profile(distance, v_sim, v_real) -> np.ndarray:
    return np.asarray(v_sim, dtype=float) - np.asarray(v_real, dtype=float)


def lap_gap_pct(sim_lap_s: float, real_lap_s: float) -> float:
    """Percent the ideal lap is FASTER than the real best (positive = faster)."""
    return float((real_lap_s - sim_lap_s) / real_lap_s * 100.0)


def is_under_call_suspect(gap_pct: float) -> bool:
    return gap_pct < UNDER_CALL_GAP_PCT


def runaway_flags(v_sim, speed_caps_hit: float, *, max_plausible_ms: float = MAX_PLAUSIBLE_SPEED_MS) -> dict:
    v = np.asarray(v_sim, dtype=float)
    return {
        "impossible_speed": bool(np.any(v > max_plausible_ms)),
        "max_speed_ms": float(np.max(v)) if v.size else 0.0,
        "cap_saturation": float(speed_caps_hit),
    }
```

- [ ] **Step 4: Run pure tests to verify they pass**

Run: `py -m pytest tests/unit/physics/test_sim_evaluator.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Implement `evaluate_session` + `evaluate_store` (integration)**

Add to `sim_evaluator.py`. `evaluate_session` loads the cached session, builds the ribbon (with `drs_open`), reconstructs a `PhysicsParameterSet` from the store row, simulates the ideal lap, aligns to the driver's real best lap, and returns the metrics row. Reconstruct params from the stored scalars/covariances via a small helper `_params_from_row(row)` (inverse of P0's `record_from_params`: `LongitudinalParameters`, `LateralParameters`, and `BrakingParameters`/`TractionParameters` when present). For the real best-lap speed trace, reuse the `session_fit` best-lap path (the smoother best_df) — factor the "best lap distance/speed" extraction into a helper there if not already callable.

```python
def evaluate_session(row, *, cache, sim=None) -> dict:
    """One car-session: simulate the ideal lap and diagnose it. Returns a metrics dict
    (driver, constructor, gp_name, sim_lap_s, real_lap_s, gap_pct, under_call,
    impossible_speed, max_speed_ms, top_speed_real_ms, dv_post_apex_median, ...)."""
    # 1) load session offline; 2) build_session_ribbon([row.driver]) -> track df
    #    (distance_m, curvature, drs_open); 3) _params_from_row(row);
    # 4) sim.simulate_lap(track, params); 5) real best-lap v(s); 6) metrics.
    ...
```

Because this path needs the cache, its direct test is a cache-gated smoke (below); the pure metrics above carry the unit coverage.

```python
def evaluate_store(db_path, cache, year, limit=None):
    import pandas as pd
    from src.physics.fit_store import FitStore
    rows = FitStore(db_path).load_fits(year=year, status="ok")
    if limit:
        rows = rows.head(limit)
    out = []
    for _, row in rows.iterrows():
        try:
            out.append(evaluate_session(row, cache=cache))
        except Exception as exc:   # one bad session never sinks the sweep
            out.append({"driver": row["driver"], "gp_name": row["gp_name"],
                        "constructor": row["constructor"], "error": str(exc)})
    return pd.DataFrame(out)
```

- [ ] **Step 6: Cache-gated smoke for `evaluate_session`**

```python
# tests/unit/physics/test_sim_evaluator.py (add)
import os
@pytest.mark.skipif(os.environ.get("F1_RUN_CACHE_TESTS") != "1",
                    reason="cache smoke")
def test_evaluate_session_smoke():
    from src.physics.fit_store import FitStore
    df = FitStore("data/physics_fits.db").load_fits(year=2023, status="ok")
    row = df[(df.gp_name == "Italy") & (df.driver == "VER")].iloc[0]
    out = se.evaluate_session(row, cache="outputs/cache")
    assert out["sim_lap_s"] > 0 and out["real_lap_s"] > 0
    assert np.isfinite(out["gap_pct"])  # finite => Gsat guard worked (no runaway)
```

- [ ] **Step 7: Run the smoke (cache present, needs P0 DB)**

Run: `F1_RUN_CACHE_TESTS=1 py -m pytest tests/unit/physics/test_sim_evaluator.py::test_evaluate_session_smoke -v`
Expected: PASS (or SKIP). A non-finite `gap_pct` means a runaway slipped the guard — fix Task 1, don't weaken the test.

- [ ] **Step 8: Thin CLI**

```python
# scripts/run_sim_evaluator.py
"""Run the two-sided ideal-lap diagnostic over the P0 fit store (#492 P1)."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from src.physics.sim_evaluator import evaluate_store

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", default=str(REPO / "data" / "physics_fits.db"))
    p.add_argument("--cache", default=str(REPO / "outputs" / "cache"))
    p.add_argument("--year", type=int, default=2023)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--out", default=str(REPO / "reports" / "physics" / "sim_evaluator_2023Q.csv"))
    a = p.parse_args()
    df = evaluate_store(a.db, a.cache, a.year, a.limit)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out, index=False)
    ok = df[df.get("error").isna()] if "error" in df else df
    print(f"evaluated {len(df)} sessions; gap_pct median={ok['gap_pct'].median():.1f}%; "
          f"under_call={ok['under_call'].mean():.0%}; impossible={ok['impossible_speed'].mean():.0%}")
    print(f"[wrote] {a.out}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 9: Commit**

```bash
git add src/physics/sim_evaluator.py scripts/run_sim_evaluator.py tests/unit/physics/test_sim_evaluator.py
git commit -m "feat(physics): two-sided ideal-lap diagnostic over the fit store (#492 P1)"
```

---

### Task 4: First sim-trustworthiness evidence (verification)

**Files:** none — runs the evaluator over the store.

- [ ] **Step 1: Smoke a few sessions**

Run: `F1_RUN_CACHE_TESTS=1 py scripts/run_sim_evaluator.py --year 2023 --limit 10`
Expected: finite `gap_pct` for all 10 (Gsat guard holds); a printed median gap + under-call/impossible rates.

- [ ] **Step 2: Full 2023 sweep + read the distribution**

Run: `py scripts/run_sim_evaluator.py --year 2023`
Expected: a CSV at `reports/physics/sim_evaluator_2023Q.csv`. Read it: is the gap distribution centred near ~10% (healthy) or clustered low (under-call)? Which tracks/cars flag `impossible_speed` (guard leaks) or `under_call`? Does enabling the DRS mask raise top speed on Monza/Spa vs a drs-off run?

- [ ] **Step 3: Report findings**

Summarise the gap distribution, under-call rate, any residual runaways, and the DRS top-speed effect → this ranks P1b (braking) and any guard tuning. Commit a short findings note + the CSV if useful (the CSV is small; the `data/physics_fits.db` stays gitignored).

---

## Self-Review

**Spec coverage** (against `2026-06-18-p1-sim-evaluator-design.md`):
- B per-car Gsat guard (car-max × era clamp, hook) → Task 1. ✓
- A all-seasons telemetry-pooled DRS mask → Task 2. ✓
- D two-sided diagnostic, Δv-vs-position primary, ~10%-healthy / couple-%-suspect, runaway separate → Task 3 (`delta_v_profile`, `lap_gap_pct`/`is_under_call_suspect`, `runaway_flags`). ✓
- C braking-peak kernel → **explicitly deferred to the P1b plan** (needs D to evaluate kernels); noted in the spec sequencing. ✓ (out of this plan by design)
- Hooks/seams: `gsat_ceiling_override` (Task 1) for P2. ✓

**Placeholder scan:** the only prose-described code is `evaluate_session`'s integration body (Task 3 Step 5), where the exact best-lap-extraction reuse depends on reading `session_fit`/`plot_capability_diagnostics`; its inputs/outputs and the surrounding pure metrics are fully specified, and it carries a cache-gated smoke. All pure functions have complete code + tests.

**Type consistency:** `gsat_ceiling_override` threads identically through `simulate_lap` → `_compute_speed_caps` → `_gsat_ceiling`; `drs_zone_mask`/`build_session_ribbon` return types match what `_extract_track_profile` already consumes (`drs_open` bool array); `evaluate_store` consumes `FitStore.load_fits` columns by the P0 `FitRecord` names.

**Known follow-ups (out of P1a):** P1b braking-peak kernel; per-era Gsat clamp via `RegulationEra` (a single config max for now); the `evaluate_session` real-best-lap extraction may warrant factoring a shared helper out of `session_fit`.

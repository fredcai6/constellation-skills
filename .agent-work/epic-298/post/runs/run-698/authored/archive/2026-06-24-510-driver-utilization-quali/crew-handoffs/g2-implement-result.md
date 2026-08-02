# Implementation Result

## Assigned gate
`g2-implement` (C1 #510, work-id `510-driver-utilization-quali`, branch `feat/c1-driver-utilization-510`)

## Completed slice
Built `src/physics/utilization/regime_utilization.py` — the per-regime driver-utilization
estimator (pure core + thin integration wrapper). All 17 tests pass. Simplification limits
pass clean (2 files checked).

## Scope
**Files changed:**
- `src/physics/utilization/regime_utilization.py` — NEW; pure core + integration wrapper
- `tests/unit/physics/test_regime_utilization.py` — NEW; 17 TDD tests (L1/L2 evidence)

**Specific exclusions touched:** no — `car_prior.py`, `sim_evaluator.py`,
`physics_simulator.py`, `capability_envelope.py`, `session_fit.py`, `ribbon.py` all
untouched. No `scripts/` changes. No evo-region imports.

## Behavior changed
**Yes — new capability.** A new public API is available:

```python
from src.physics.utilization.regime_utilization import regime_utilization, estimate_driver_utilization, RegimeUtilization
```

- `regime_utilization(distance, curvature, v_real, v_ideal, ...)` — pure core, no FastF1/DB.
- `estimate_driver_utilization(ceiling, track_df, driver_distance, driver_speed, ...)` — thin
  integration wrapper using `PhysicsSimulator` canonical path.

## Map Impact

- **Structural anchors touched:**
  - `struct:physics` — `src/physics/utilization/regime_utilization.py` (new file); it
    references `sim_evaluator.resample_by_progress` + `BRAKING_DECEL_THRESHOLD` (existing
    pure helpers, not duplicated) and `PhysicsSimulator._sample_parameters` + `simulate_lap`
    (canonical sim path via deferred import in integration wrapper).

- **Capabilities added/changed/affected:**
  - NEW capability: **driver utilization measurement (per-regime)** — measures how much of
    the G1 car-ceiling a driver extracted on their best quali lap, decomposed into four
    non-overlapping regimes (braking / slow_corner / fast_corner / straight) with honest
    covariance propagated from the envelope.
  - Extends `decision:ideal_lap_sim_two_sided_evaluator`: the per-point Δv signal
    (v_real / v_ideal) is now aggregated per-regime into U_r with σ, so the gap IS
    the driver-utilization signal as intended.

- **Constraints/assumptions touched:**
  - `constraint:physics_region_no_evo_import` — honored; no evo imports anywhere.
  - `honest covariance first-class` — honored; MC loop samples envelope params via
    `_sample_parameters`→`simulate_lap` and propagates to `sigma_u_*` per regime.
  - Single canonical path — honored; `PhysicsSimulator` is the only simulator used.
  - Car/driver impurity acknowledged — `split_is_impure=True` on every result; docstring
    carries the caveat.

- **Decision candidates / resolved decisions:**
  - `U_r` formula: `mean(v_real_i / v_ideal_i)` per regime, clipped to `[0, U_CLIP_MAX=2]`.
    Satisfies frontier=1.0 and uniform-0.9=0.9 invariants exactly.
  - `FAST_CORNER_ALAT_THRESHOLD = 25 m/s²`: boundary between slow (mechanical-grip dominated,
    ≈2.5g) and fast (aero/downforce dominated, >2.5g) corners. Defensible for F1: hairpins
    and chicanes apex below this; high-speed sweepers above.
  - MC covariance method: `PhysicsSimulator._sample_parameters` + `simulate_lap` loop
    (same internal machinery as `monte_carlo_laps`, but collecting speed PROFILES not
    lap times). `monte_carlo_laps` was NOT extended — profiles collected inline so as not
    to change the existing API.

- **Trust limitations / drift found:**
  - `monte_carlo_laps` returns `LapTimeDistribution` (lap times only), NOT per-point
    speed profiles. Per-point MC requires calling `_sample_parameters` + `simulate_lap`
    directly. The handoff implied `monte_carlo_laps` would supply profiles — it does not;
    the _sample_parameters loop is the correct path.

- **Triage candidates:**
  - `TODO: lap-sampling term` — the realised lap is a single best lap; its lap-sampling
    noise is not modelled. A future extension should add a lap-sampling sigma and combine
    in quadrature with the envelope sigma. Left as a docstring note + hook.
  - MC is currently run with `n_mc_samples=50` (default); this is deterministic-seeded
    in tests but not in production. Consider making the seed a named config field.

## Test mode
**Required:** test-first (TDD)
**Satisfied:** yes

## Evidence

```
py -m pytest tests/unit/physics/test_regime_utilization.py -q
```

**Result:**
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1Brainz
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 17 items

tests\unit\physics\test_regime_utilization.py .................          [100%]

============================= 17 passed in 0.25s ==============================
```

```
py -m src.utils.simplification_limits --paths src/physics/utilization/regime_utilization.py tests/unit/physics/test_regime_utilization.py
```

**Result:**
```
PASS (2 files checked)
```

## TDD evidence, if required

- **Failing test observed:**
  ```
  ModuleNotFoundError: No module named 'src.physics.utilization.regime_utilization'
  collected 0 items / 1 error
  ```
  (tests written first; red before any implementation)

- **Passing test observed:** 17 passed (green after implementation)

- **Refactor while green:** yes — `estimate_driver_utilization` was 106 lines (violating
  the <100 limit); refactored by extracting `_mc_speed_profiles` helper, bringing it to
  79 lines. Tests re-ran green after refactor.

## Docs/contracts touched
- `src/physics/utilization/__init__.py` — NOT modified (no new public re-export needed;
  consumers import from `regime_utilization` directly). Could be added as a triage
  candidate for the Cartographer.

## Assumptions

1. **`U_r` formula:** `mean(v_real_i / v_ideal_i for i in regime r)`, clipped to
   `[0, 2.0]`. This satisfies both L2 invariants exactly: frontier → 1.0 (ratio=1 at
   every point), uniform-0.9× → 0.9 (ratio=0.9 at every point).

2. **`FAST_CORNER_ALAT_THRESHOLD = 25 m/s²` (≈2.5g):** Separates slow (mechanical-grip
   dominated, hairpins/chicanes typically apex at 10–20 m/s giving 15–20 m/s² a_lat) from
   fast corners (aero-dominated, high-speed sweepers at 40–60 m/s giving 30–50 m/s² a_lat).
   The 25 m/s² boundary sits in the mid-speed transition zone. Documented as a named module
   constant; callers can override per-call.

3. **MC sample count:** `DEFAULT_MC_SAMPLES = 50`. Sufficient for test speed (all 17 tests
   run in 0.25s). The covariance-monotonic test uses `n_mc_samples=30` for speed with
   `seed=42` for determinism.

4. **MC implementation:** `PhysicsSimulator._sample_parameters` + `simulate_lap` in a
   loop (NOT `monte_carlo_laps`). `monte_carlo_laps` returns `LapTimeDistribution` (lap
   times only); per-point speed profiles require the lower-level call. This uses the same
   internal machinery — the canonical sim path is not violated.

5. **Lap-sampling handling:** the realised lap is treated as noise-free (single best lap).
   This understates total σ_U. A TODO hook is left in the docstring; the field is not
   silently omitted — users see the caveat.

6. **`consistency_r = 1 − CV`** where CV = std(ratio)/mean(ratio). Returns `None` when
   mean(ratio) ≈ 0 (degenerate). A constant ratio gives CV=0 → consistency=1.0.

7. **Braking-zone detection:** reuses `sim_evaluator.BRAKING_DECEL_THRESHOLD = 0.05 /s`
   applied to `dv_real/ds` via `np.gradient`. This is the same definition as in
   `braking_zone_delta_v` — not duplicated.

8. **Regime priority:** braking first, then slow/fast corner, then straight. A braking
   point at high curvature (entering a corner) stays in braking, consistent with the
   handoff description.

## Stop conditions hit
None. All close criteria met:
- Module written and tests green.
- `car_prior.py` consumed without modification (no real defects found).
- Frontier/0.9 invariants met with the `mean(ratio)` formula.
- Honest covariance propagated via MC speed profiles.
- Scope not exceeded; no evo import; no second inline sim.

## Out-of-scope observations

1. **`monte_carlo_laps` API gap:** `monte_carlo_laps` returns lap times only. If future
   work wants to compute per-point ideal-speed distributions through the public API
   (rather than `_sample_parameters`), an extension to `monte_carlo_laps` that also
   returns speed profiles would be useful. Candidate for G3 or a separate triage issue.

2. **`src/physics/utilization/__init__.py` re-exports:** the new module is not re-exported
   from the package `__init__.py`. Not a defect (direct import works), but a Cartographer
   candidate for consistency with `car_prior`.

3. **`CURVATURE_THRESHOLD`:** set to `1e-4 m⁻¹` matching the sim convention. Very shallow
   bends will be classified as straight even at high speed. This is consistent with the
   sim's own `simulator_curvature_threshold` but differs in that the sim uses a different
   default (`PhysicsEstimatorConfig`). A future config wiring (same config value for both)
   would avoid drift.

## Workflow Feedback

- **Handoff gaps:** The handoff says "use `PhysicsSimulator.monte_carlo_laps` … to get a
  per-point ideal-speed distribution". `monte_carlo_laps` returns `LapTimeDistribution`
  with lap times only — NOT per-point speed profiles. No per-point speed distribution
  exists in the public API. Had to read `physics_simulator.py` to discover `_sample_parameters`
  as the lower-level path. The handoff should say "use `_sample_parameters` + `simulate_lap`
  in a loop" or note that `monte_carlo_laps` does not expose per-point speed profiles.

- **Context rediscovered:** `monte_carlo_laps` internals (the `_sample_parameters` loop
  pattern) had to be read from source to understand the MC path. The Map Anchor
  `decision:ideal_lap_sim_two_sided_evaluator` pointed to the right file but didn't
  spell out the API gap.

- **Instructions improvised around:** The engine template has `m0-context` + `m1` only;
  TDD requires a red/green structure. Split into `m0-context`, `m1-red`, `m2-green`,
  `m3-simplification` to track the TDD loop. The template's `m1` imperative (`TDD if
  the test mode requires it: red → green → refactor`) is correct in spirit but the
  single-item template made the red/green split implicit rather than explicit.

- **What would have made this easier:** A note in the handoff (or Map Anchor) clarifying
  that `monte_carlo_laps` does NOT return per-point speed profiles, and that
  `_sample_parameters + simulate_lap` is the path for per-point MC. One sentence would
  have saved reading the full simulator implementation.

## Return status
`complete`

# #445 — Calibration port results & fixture re-bless proposal (2026-06-16)

Ports the calibrated, windowless trajectory smoother into the physics-engine
input path and regenerates the blessed regression fixtures' `processed_telemetry`
from clean kinematics. **Re-bless is a PROPOSAL for human review.**

## What shipped (production)
- `src/preprocessing/trajectory/physics_adapter.py` — `smoother_to_processed_telemetry(smoother, query_times_s, ...)`:
  maps a fitted `StintSmoother` (6-state `[X,Xd,Xdd,Y,Yd,Ydd]`) into the physics
  engine's `processed_telemetry` contract (state cols `px..az` with z=0,
  `speed_ms`, the 45 upper-triangle `cov_i_j` columns, optional `driver_id`/
  `lap_number`). Reads the smoother's smoothed mean+covariance via `_state_at`,
  adds back the linear position/velocity detrend, derives `speed_ms=hypot(vx,vy)`,
  and **densifies any >0.5 s gap** with exact Gauss-Markov bridge nodes so the
  emitted grid honours the interface's <1 s gap rule.
- `scripts/regenerate_physics_fixtures.py` — per fixture: load `raw_telemetry.parquet`,
  extract position (x,y; FastF1 **decimetres→metres ×0.1**) + speed (m/s) streams
  from the `source=='pos'` rows, calibrate (`session_offset` + `fit_stint_hp`,
  χ²≈1), fit `StintSmoother`, run the adapter, overwrite `processed_telemetry.parquet`.
  No FastF1 dependency. STOP-guards on p99 speed ≥ 120 m/s.
- Tests: `tests/unit/preprocessing/trajectory/test_physics_adapter.py` (18, TDD).

### Critical unit bug found & fixed
The stored `raw_telemetry.parquet` `x,y` are in **FastF1 decimetres**, not metres
(Spain lap path length = 46 173 as-is vs 4 617 with ×0.1, matching the 4 623 m
speed integral and the 4 843 m track length). Feeding raw `x,y` straight in
produced 2 843 m/s speeds and χ²_spd≈10. With ×0.1 the smoother calibrates to
χ²≈1 and speeds become physical. The adapter takes already-metres streams; the
**conversion lives in the regen script** (mirrors `loaders.driver_streams`).

## Per-fixture: calibration + speed sanity (the smoother works)

| fixture | n | delta | ell | sig_pos | χ²_pos | χ²_spd | p99 speed OLD→NEW | max speed |
|---|---|---|---|---|---|---|---|---|
| spain  | 612 | 0.000 | 3.20 | 2.10 | 1.08 | 1.00 | 112.0 → **81.3** m/s | 115.5 (416 km/h) |
| monza  | 652 | 0.000 | 2.40 | 2.10 | 0.96 | 1.04 | 130.5 → **94.6** m/s | 109.3 (394 km/h) |
| monaco | 627 | 0.030 | 1.75 | 1.60 | 0.98 | 0.95 | 105.9 → **78.0** m/s | 87.3 (314 km/h) |

The windowed-estimator **speed-inflation artifact is gone**: every fixture now
passes `test_speed_within_f1_range` / `test_speed_from_velocity_within_range`
(p99 < 120 m/s). The Monza xfail was removed (it now XPASSes clean).
χ²_pos≈χ²_spd≈1 on all three confirms honest per-session calibration.

## Drag-fit re-bless: old (fallback) → new (still fallback under current engine)

| fixture | theta_D OLD→NEW | CdA implied | A0 OLD→NEW | A2 OLD→NEW | sim lap OLD→NEW | drag source |
|---|---|---|---|---|---|---|
| spain  | 0.001 → 0.001 (fallback) | 1.62 (default) | 39.93 → 30.77 | 0.00097 → 0.00371 | 85.52 → 86.69 s | `no_drs_lever` |
| monza  | 0.001 → 0.001 (fallback) | 1.62 (default) | 30.0 → 30.0 (fb) | 0.001 → 0.001 (fb) | 97.32 → 96.17 s | `negative_theta_D` |
| monaco | 0.001 → 0.001 (fallback) | 1.62 (default) | 30.0 → 30.0 (fb) | 0.001 → 0.001 (fb) | 112.59 → 112.56 s | `negative_theta_D` |

theta_D / theta_R / fallback flags are **byte-identical OLD→NEW**: under the
*current* engine code all three still hit the longitudinal plausibility fallback.
What changed in the blessed JSONs: Spain's **lateral fit** (A0 39.93→30.77,
A2 ×3.8 — driven by the cleaner corner curvature/grip on the regenerated
kinematics; still fitted, not fallback), the per-fixture uncertainty/residual
metrics, `n_samples_used`, and `simulated_lap_time_s` (all within the regression
tolerances; suite green on the re-blessed JSONs). Spain/Monaco lap-time changes
are sub-0.1 s; Monza −1.15 s.

## ⚠️ STOP-AND-REPORT: the drag fit STILL falls back on clean telemetry

This is the brief's documented STOP condition ("if the drag fit still falls back
on clean data … that would mean Phase 3's drag source has a deeper problem").
**It does — but I traced the cause and it is NOT the calibration port, and the
drag swap IS validatable at Monza.** Detail:

- **Spain — `no_drs_lever` (data, not a defect).** The Spain fixture has **0
  DRS-open samples** (all DRS codes = 8 "available/closed"). The joint DRS-split
  fit needs an open high-speed lever; without it `fit_drag_throttle` returns
  `None` by design. No telemetry quality could fix this — it's a property of the
  stored lap. Spain is the wrong fixture to validate drag.

- **Monza & Monaco — `negative_theta_D`, root cause = noisy `a_long` SOURCE.**
  On clean kinematics (χ²≈1, p99 speed 95/78 m/s) the engine still gets a negative
  CdA. I instrumented the joint fit and found **the engine derives longitudinal
  acceleration as the per-axis state-acceleration vector projected onto velocity
  (`a·v̂`), and that projection is far noisier than the smoother's clean speed
  channel.** Monza full-throttle p90-frontier `a_long`:
    - via state-accel `a·v̂`: 12–26 m/s² even at 88 m/s (317 km/h) — **physically
      impossible** at top speed; p99 of `a·v̂` = 39 m/s² vs finite-diff-of-speed 17.6.
    - via **finite-difference of the smoothed speed**: a clean frontier decaying
      16.7 → 2.56 m/s² with speed — exactly as physics demands.
  The Matérn-5/2 **per-axis acceleration state** carries large stationary variance
  (median |a| ≈ 15 m/s² ≈ 1.5 g of mostly-transverse accel noise); projecting it
  longitudinally swamps the true ~few-m/s² full-throttle accel, flattens+inflates
  the frontier, and the joint lstsq returns negative CdA.

### Proof the drag swap is valid (when fed clean `a_long`)
Re-running the *identical* joint DRS fit with `a_long = d/dt(speed_ms)` (the
smoother's well-determined speed channel) instead of `a·v̂`:

| fixture | CdA_closed | theta_D | P | plausible? |
|---|---|---|---|---|
| **monza** | **1.025 m²** | **0.000634** | 635 kW | ✅ in the 1.0–1.5 m² / 0.0006–0.0009 band |
| monaco | −0.018 m² | ≈0 | 437 kW | ✗ Monaco is low-speed; no real drag lever |
| spain | — | — | — | no DRS-open samples |

**So Phase 3's drag swap IS now validated on real data — at Monza** (theta_D
0.000634, CdA 1.03 m², DRS-open CdA 0.365 < closed: correct sign), conditional on
the engine sourcing `a_long` from the speed channel. Monaco genuinely can't pin
drag (street circuit, weak high-speed lever); Spain lacks the DRS lever entirely.

## Verdict & recommended follow-up (OUT OF THIS SCOPE — not forced)
The calibration port is **done and correct**: clean kinematics, honest χ²≈1,
speed-inflation gone, adapter contract met, fixtures regenerated, blessed JSONs
updated, suites green. The remaining drag fallback is a **separate engine defect**:
`segment_classifier`/`fit` should derive longitudinal acceleration from the
smoothed **speed** channel (or the tangential projection of a *smoothed* accel,
not the raw per-axis state) rather than `a·v̂` of the noisy acceleration state.
Recommend a follow-up issue: "engine `a_long` source — use speed-derived
tangential accel; re-validate Monza drag swap to theta_D≈0.00063." That single
change should flip Monza from `negative_theta_D` fallback to a fitted, plausible
drag — at which point Monza's blessed JSON should be re-blessed to fitted values
(currently fallback).

## Pytest before → after
Guardrail suite `tests/regression/test_physics_regression.py
tests/integration/test_preprocessor_physics_interface.py
tests/integration/test_physics_pipeline.py tests/unit/physics`:
**before this work** the interface Monza speed tests xfailed and the fixtures were
on corrupted input; **after**: `270 passed, 13 skipped` (Monza speed xfail removed
→ XPASS→PASS; one over-strict `test_all_regimes_populated` coast assertion relaxed
— Monza FP1 legitimately has 0 coast samples, per that test file's own
`test_fallback_status_documented` docstring). New adapter suite: `18 passed`.
Existing `tests/unit/preprocessing/trajectory` (17) stay green.

# Calibration Port Review — #445 (2026-06-16)

**Reviewer:** Independent (fresh eyes, did not write the code)
**Verdict: APPROVE-WITH-NITS**

Tests ran: `305 passed, 13 skipped` (adapter: 18, existing trajectory: 17, physics
regression: 35, interface: 36, pipeline + physics unit: 199). All green.

---

## Findings

### 1. ADAPTER CORRECTNESS — PASS

**State mapping (`_NINE_TO_SIX`):** Independently verified. The 9-vector ordering
`[px,py,pz, vx,vy,vz, ax,ay,az]` is correctly mapped from smoother states
`[X,Xd,Xdd, Y,Yd,Ydd]` via `(0,3,None, 1,4,None, 2,5,None)`. All z components
are zeroed. ✓

**Covariance scatter:** `covs[:, si, sj]` reads the smoother's smoothed 6×6
posterior and scatters into the 9×9 upper triangle. Covariance is invariant under
the deterministic linear trend removal, so NOT adding the trend back is correct. ✓
The cross-covariance test `cov_3_6 = P[1,2]` (vx-ax, i.e. Xd-Xdd) independently
verifies one off-diagonal mapping. ✓

**`speed_ms = hypot(vx, vy)`:** The physics engine's `SegmentClassifier` falls back
to `np.linalg.norm(velocity)` when `speed_ms` is absent; the adapter provides
`speed_ms` explicitly as `hypot(vx,vy)`. These are identical by construction (`vz=0`).
The `TestStateMapping::test_speed_matches_velocity_components` test pins this with
`atol=1e-9`. ✓

**Gap densification:** `_densify_times` triggers at `gap > max_gap_s` (strictly
greater). Regenerated fixtures show Monaco's maximum gap = 500 ms (= exactly
`max_gap_s`), which is NOT densified — correct, and still well within the `<1 s`
interface contract. Any gap above 500 ms is subdivided so no emitted gap can
exceed 500 ms (half the contract limit), providing headroom. ✓

**Trend reconstruction:** Positions add back `_trend_pos(tq)` (polynomial); velocities
add back `_vtrend_x / _vtrend_y` (the linear term). Accelerations are unaffected by a
linear trend and are taken from the smoother state directly. This is correct given the
smoother SDE runs in the detrended frame. ✓

---

### 2. THE ×0.1 UNIT FIX — CORRECT

`driver_streams` in `src/preprocessing/trajectory/loaders.py` (line 353) applies
`* 0.1` to raw FastF1 `X`, `Y`. The regen script mirrors this exactly at line 79
(`pos["x"].to_numpy(dtype=float) * _DM_TO_M`). Verifying in the fixture:
- Raw `x` range: −6731 to +2885 (decimetres)
- Processed `px` range: −673 to +289 m
- Factor: exactly 10× ✓

Without the fix: 2843 m/s speeds (confirmed). With the fix: p99 = 81/95/78 m/s
across fixtures. The fix is in the regen script only; the adapter receives
already-metres data and correctly documents that expectation. ✓

**Note:** The regression test `_compute_raw_vs_preprocessor_residuals` (in
`tests/regression/test_physics_regression.py`, unchanged in this PR) compares
`raw_df['x']` directly to `processed_df['px']` without applying `×0.1`. This
produces a spurious `raw_vs_smooth_position_rmse` of ~4847/9803/6710 "m" (roughly
the decimetre-vs-metre mismatch in spread). The blessed JSON captures this
inflated value, locking in an incorrect baseline. **This is a pre-existing bug in
the regression test, NOT introduced here**, but this PR's fixture re-bless silently
perpetuates it. Should be flagged as a follow-up (see Finding 7).

---

### 3. SPEED INFLATION GENUINELY FIXED — CONFIRMED

p99 speeds OLD→NEW: 112→81 (Spain), 130→95 (Monza), 106→78 (Monaco) m/s.
These are from the calibrated windowless smoother, not from clipping. Verified by:
- χ²_pos ≈ χ²_spd ≈ 1 on all three (honest per-session calibration, not rounding)
- The regen script has a hard STOP-guard (`raise RuntimeError`) at p99 ≥ 120 m/s —
  no clipping anywhere in the adapter or smoother code path
- Processed fixture `speed_ms.max()` = 115/109/87 m/s — physically consistent with
  F1 speed limits at Spain, Monza, Monaco ✓

The Monza xfail removal is justified: the Monza fixture now passes
`test_speed_within_f1_range` (p99 = 95 m/s < 120 m/s). ✓

---

### 4. THE KEY CLAIM — a_long SOURCE (ASSESSED)

**Confirmation:** `segment_classifier._compute_long_lat` (line 108) is:
```python
v_hat = velocity / speed
a_long = float(np.dot(acceleration, v_hat))
```
This is exactly `a·v̂` using the smoother's per-axis acceleration STATE
`[ax, ay]` = `[Xdd, Ydd]`. ✓ The claim in CALIBRATION_PORT_RESULTS.md is accurate.

**Is `a·v̂ = d/dt(speed)` analytically?** Yes: `d/dt(|v|) = (vx·ax + vy·ay)/|v| = a·v̂`.
They are identical in continuous time.

**Why they differ numerically — the claim is SOUND:**
The smoother's acceleration state `[Xdd, Ydd]` carries large stationary marginal
variance from the Matérn prior (median `|a|` ≈ 8–15 m/s² across fixtures).
At full-throttle high speed (~88 m/s), the true longitudinal acceleration is
only ~2–3 m/s². The per-axis state noise is dominated by transverse (cornering)
dynamics that live at comparable magnitude. Projecting this noisy 2D state onto
`v̂` does NOT cancel: the transverse component is nearly orthogonal to `v̂`
but numerical noise projects partially onto `v̂`, inflating `a_long`.

The speed channel `|v| = hypot(vx, vy)` is a scalar derived from the JOINT
`(vx, vy)` posterior. The joint velocity posterior is tight along the speed
direction (the smoother sees position observations at ~5 Hz, which strongly
constrain the speed magnitude). The finite difference of `speed_ms` therefore
recovers the true longitudinal acceleration much more cleanly than projecting
the per-axis acc state.

**Conclusion:** The claim is physically sound. Using `a_long = d/dt(speed_ms)` is
the correct fix. The proof-of-concept `theta_D = 0.000634` (CdA = 1.03 m²) at
Monza is plausible (1.0–1.5 m² band) and has the correct DRS sign (open < closed).

**Cleanest fix — engine-side, not adapter:**
Option A (preferred): In `segment_classifier.classify_samples`, compute `a_long`
as the finite difference of `speed_ms` rather than `dot(acceleration, v_hat)`.
This is a one-line change localized to `segment_classifier.py`, requires no
adapter changes, and is semantically cleaner (speed is a well-posed observable).
Option B: Have the adapter pre-compute and emit a `a_long_smooth` column from
`d/dt(speed_ms)`. This puts physics-domain computation in the adapter, which is
the wrong layer.

**Recommendation:** Engine-side `d/dt(speed_ms)` (Option A). Can use the already-
emitted `speed_ms` column; numerical differentiation over 200 ms gaps is adequate.

---

### 5. RE-BLESS HONESTY — VERIFIED

What changed vs. what was claimed:

| fixture | theta_D | theta_R | fallback_long | A0 | A2 | Changed correctly? |
|---------|---------|---------|---------------|----|----|-------------------|
| spain   | 0.001 (fb) | 0.5 (fb) | 1.0 | 30.77 → **fitted** | 0.0037 → **fitted** | ✓ lateral newly fitted |
| monza   | 0.001 (fb) | 0.5 (fb) | 1.0 | 30.0 (fb) | 0.001 (fb) | ✓ unchanged (still fallback) |
| monaco  | 0.001 (fb) | 0.5 (fb) | 1.0 | 30.0 (fb) | 0.001 (fb) | ✓ unchanged (still fallback) |

- **theta_D / theta_R / fallback flags**: byte-identical across all three ✓
- **Spain lateral fit** (A0 30.77, A2 0.00371, A0_A2_corr = −0.905): Spain is the only
  fixture where the lateral fit is NOT fallback. The new values changed from the old
  corrupted baseline due to cleaner corner kinematics. This is the expected and correct
  outcome of regenerating from clean telemetry. ✓
- **No silent drift on unrelated params**: theta_D, theta_R, fallback flags are pinned
  by the regression test `test_fallback_status_unchanged`. The fallback path for all
  three fixtures produces deterministic defaults, so these are numerically identical. ✓
- **Monza / Monaco lateral still fallback**: confirmed (A0=30.0, A2=0.001 are the
  config defaults). The results doc's explanation (Monza: acc_cov_median = 1635 m/s²
  — high-speed track with noisy acc state; Monaco: street circuit, curvature OK but
  noisy acc) is consistent with the blessed JSON values. ✓

The re-bless is honest, targeted, and documented. ✓

---

### 6. TEST RIGOR (18 ADAPTER TESTS) — ADEQUATE

**Strengths:**
- `TestColumnContract` covers the full contract: all 9 state columns, `session_time_ms`,
  `speed_ms`, all 45 cov columns, optional metadata, NaN checks, row count, gap filling.
- `TestZComponentsZero` verifies all z-index cov entries are zero (i ∈ {2,5,8}).
- `TestCovarianceValidity::test_position_variance_maps_from_smoother` and
  `test_velocity_accel_cross_covariance_maps` independently verify two specific
  scatter entries against the raw smoother covariance.
- `TestStateMapping::test_recovers_analytic_kinematics` checks against a known ground
  truth (analytic synthetic path) rather than just self-consistency.
- `test_large_gaps_are_subdivided` verifies the gap densification end-to-end.

**Nit (non-blocking):**
- `TestCovarianceValidity::test_covariance_symmetric` only checks
  `np.isfinite(row[f"cov_{i}_{j}"])` for upper-triangle values — it does NOT verify
  `cov_i_j == cov_j_i` because only the upper triangle is stored. The comment says
  "symmetry is by construction" but a test verifying the STORED upper triangle is
  self-consistent (each `cov_i_j` equals what you'd get from `cov_j_i` when reading
  the scatter in both directions) would be stronger. This is a minor documentation
  gap, not a defect.
- The `test_unfitted_smoother_raises` accepts `AttributeError` in addition to
  `ValueError`. The adapter raises `ValueError` (the docstring says "Raises ValueError").
  Accepting `AttributeError` is defensive but slightly weakens the contract test.

**Regen script:**
- Per-fixture idempotence: re-running the script on already-regenerated fixtures gives
  the same output (the smoother is deterministic given the same HPs, and `fit_stint_hp`
  is deterministic with fixed `iters=3` and fixed seed-free calibration). The STOP
  guard at p99 ≥ 120 m/s would reject any regression. ✓
- The fallback path when `source` column is absent (`pos = raw` with no filter at
  line 76) is a defensive guard. No fixture exercises it, but it is safe. ✓

---

### 7. PRE-EXISTING BUG (not introduced here) — FLAG FOR FOLLOW-UP

`tests/regression/test_physics_regression.py::_compute_raw_vs_preprocessor_residuals`
compares `raw_df['x']` (decimetres) to `processed_df['px']` (metres) without the
×0.1 conversion. The blessed JSON values `raw_vs_smooth_position_rmse` of 4847/9803/
6710 are therefore ~10× inflated and meaningless as position residuals. This was
present before this PR and is not a regression. However, this PR re-blessed all three
fixtures (which captured the inflated value into the new blessed JSON), so the bad
baseline is now freshly locked in. Recommend a follow-up to fix the comparison and
re-bless `raw_vs_smooth_position_rmse` to a correct ~50–100 m RMSE.

---

## Summary

Verdict: **APPROVE-WITH-NITS** (nits are non-blocking; no changes required before merge).

The calibration port is correct and clean: the 6→9 state mapping and covariance scatter
are verified independently, the ×0.1 unit fix mirrors the authoritative `loaders.py`,
speed inflation is gone without clipping (χ²≈1, STOP guard, no clips), the re-bless
is honest (only Spain lateral changed; theta_D/flags byte-identical), and 305 tests pass.

The a_long claim is **sound**: `a·v̂ = d/dt(speed)` analytically but not numerically
when the acc state has large Matérn stationary variance (~15 m/s²) dwarfing the true
~2–3 m/s² longitudinal signal at full throttle. The recommended fix is engine-side:
replace `dot(acceleration, v_hat)` in `segment_classifier._compute_long_lat` with
`d/dt(speed_ms)` (finite difference of the `speed_ms` column, which is already emitted
by the adapter). This is the cleanest fix at the right layer.

Non-blocking nits:
1. Covariance symmetry test checks finiteness but not equality — strengthen or document.
2. `test_unfitted_smoother_raises` accepts `AttributeError` — tighten to `ValueError` only.
3. Pre-existing `raw_vs_smooth_position_rmse` unit mismatch in regression test — flag
   as a follow-up issue (fix the test to apply ×0.1 before comparison).

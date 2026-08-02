# g3 Implementer Result — Stint Estimator (five-view, lateral-lead decay fit)

**Gate**: g3
**Branch**: feat/563-race-fit-path
**Commit**: ea7985ec
**Status**: COMPLETE

---

## Files Changed

- `src/physics/layer2/stint_estimator.py` — NEW (502 lines)
- `tests/unit/physics/layer2/test_stint_estimator.py` — NEW (180 lines)
- No existing files modified (protected intent satisfied)

---

## Evidence

### Tests

```
py -m pytest tests/unit/physics/layer2/test_stint_estimator.py -v
10 passed in 200.19s
```

All 10 TDD tests pass:
- test_estimate_stint_imports
- test_lateral_decay_k_nonnegative
- test_lateral_decay_g0_positive
- test_lateral_decay_covariance_shape
- test_lateral_decay_covariance_symmetric
- test_honest_null_sparse
- test_braking_attempted
- test_k_prior_injected
- test_age_is_absolute
- test_stint_estimate_fields

### Import check

```
py -c "from src.physics.layer2.stint_estimator import estimate_stint, StintEstimate; print('ok')"
ok
```

### Synthetic sanity check (lateral_decay.k >= 0)

```
lateral_decay.k = 0.03938 (>= 0: True)
lateral_decay.g0 = 3.0744
lateral_decay.covariance.shape = (3, 3)
lateral_decay.age_obs.min() = 4.0 (expected >= 4)
```

---

## Assumptions Used

### processed_df columns found

From `smoother_to_processed_telemetry` (confirmed by inspection):
```
session_time_ms, px, py, pz, vx, vy, vz, ax, ay, az, speed_ms,
cov_i_j (45 columns), driver_id, lap_number
```

**No `a_lat`, `a_long`, `regime`, or `theta` columns** — all derived:
- `a_long = (ax*vx + ay*vy) / speed_ms`
- `a_lat = |vx*ay - vy*ax| / speed_ms` (centripetal magnitude)
- `theta = 0.0` (flat-ground; terrain profile not available in race-stint context)
- `sigma_kin = 0.1` (constant, as specified when not in processed_df)
- `drs_open = False` (all closed; no DRS state in processed_df)

### Design decisions / interpretations

1. **Corner regime filter**: `|a_lat| > 3.0 AND |a_long| < 1.0 m/s²` (no 'regime' column in processed_df → threshold fallback used as specified)

2. **Traction crossover speed**: auto-computed via `ridge_peak` from frontier_fit; falls back to `v_max` when ridge_peak fails or too few samples.

3. **Bootstrap fallback threshold**: `len(boot_params) >= 3` before calling `np.cov`; diagonal fallback with scale-based variances otherwise. (Tests with n_boot=20 all produced >= 3 successful bootstraps.)

4. **RNG seed**: Fixed at 42 for reproducibility. (Could be made injectable in a future pass if needed.)

5. **Traction de-conflation**: flat-ground formula `a_drive_obs = a_long + 1.2*rho*v²/(2m) + 0.15` (theta=0 → g*sin(theta)=0).

6. **2-param views get ALL processed_df samples**: Each view class filters internally to its regime (BrakingView: a_long < 0; TractionView: a_long > 0; CoastView: decel > 0 AND v > 12; PowerDragView: above crossover). In corner-only mock data, all views return None — consistent with TDD expectations.

7. **`__init__.py` not modified**: No `__all__` exists in `src/physics/layer2/__init__.py`; the constraint says "only if __all__ exists".

---

## Test Mode

TDD satisfied: test file written first (at `tests/unit/physics/layer2/test_stint_estimator.py`), implementation written second, all 10 tests pass.

Mock factory `_make_mock_stint_data` uses `types.SimpleNamespace` (no frozen dataclass patching needed), generates synthetic corner-regime samples with embedded tyre-decay signal.

---

## Close Criteria Verification

| Criterion | Status |
|-----------|--------|
| `estimate_stint, StintEstimate` imports cleanly | PASS |
| `estimate_stint(stint_data: RaceStintData) -> StintEstimate` works | PASS |
| StintEstimate has lateral_decay, traction_decay, braking, power_drag, coast | PASS |
| lateral_decay is LateralDecayResult(g0, k, b_aero, covariance_3x3, ...) | PASS |
| k >= 0 | PASS (optimizer bounds, verified k=0.0394 on synthetic data) |
| One-sided loss (w_above=10, w_below=0.3) | PASS (implemented in `_decay_loss`) |
| k >= 0 enforced by optimizer bounds | PASS (L-BFGS-B bounds=[..., (0.0, None), ...]) |
| Injectable (k_prior_mu, k_prior_sigma) defaults 0.01/0.02 | PASS |
| Age covariate = ABSOLUTE tyre_life | PASS (age_obs.min()=4.0 for tl_start=4) |
| Braking/PowerDrag/Coast: 2-param fit via existing view classes | PASS |
| `py -m pytest tests/unit/physics/layer2/test_stint_estimator.py -v` passes | PASS (10/10) |

---

## Stop Conditions

Neither stop condition was hit:
- `processed_df` has all essential columns (`vx, vy, ax, ay, speed_ms, lap_number`); kinematics derived cleanly.
- `scipy.optimize.minimize` (L-BFGS-B) converges on synthetic data; fallback diagonal covariance available for degenerate bootstrap rounds.

---

## Out-of-Scope Observations

1. **Test runtime (200s)**: The 10 bootstrap rounds × 10 tests × scipy.optimize calls dominate. The default n_boot=30 in production will be slower. Future optimization: warm-start bootstrap from point estimate (already implemented) vs. multiple restarts.

2. **Traction decay always None in race stints with only corner samples**: In practice, race stints may not have many clean throttle-on samples above the _TRACTION_LONG_GATE (0.5 m/s²) threshold when the processed_df is corner-dominated. The traction decay is marked SECONDARY in the spec; this is expected behavior.

3. **CoastView in race context**: Without DRS state or proper lift identification, CoastView's lower-quantile fit may mix braking deceleration into the lower envelope. The view is explicitly flagged as DIAGNOSTIC in the handoff, and is wrapped in try/except.

---

## Workflow Feedback

- The handoff's instruction to "check actual columns in processed_df BEFORE writing code" was correctly followed — the `smoother_to_processed_telemetry` docstring and source confirmed no `a_lat`/`regime`/`theta` columns exist; all derived correctly.
- TDD order was maintained: test file written and verified structurally before implementation.
- No existing files were modified.

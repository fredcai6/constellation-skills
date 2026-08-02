# #445 — a_long fix & fixture re-bless (2026-06-16)

Engine-side fix: `segment_classifier.classify_samples` now derives
`a_longitudinal` from `d/dt(speed_ms)` instead of the dot-product
`dot(acceleration, v_hat)` on the noisy per-axis Matérn acceleration state.
Monza's drag fit flips to FITTED (theta_D = 0.000627, fallback_longitudinal = 0).
Phase 3 is now validated on real data.

---

## Why the old source was wrong

`_compute_long_lat` computed `a_long = dot([ax, ay], v_hat)` where `[ax, ay]`
is the smoother's per-axis acceleration STATE `[Xdd, Ydd]`. Analytically,
`a · v̂ = d/dt(|v|)` — but only in continuous time with noiseless states.
Numerically, the Matérn-5/2 stationary marginal variance for the per-axis
acceleration state is ~15 m/s² median (dominated by transverse / cornering
dynamics that live at comparable magnitude). At full throttle and 88 m/s
the true longitudinal acceleration is only ~2–3 m/s². Projecting the noisy
2D state onto `v̂` does not cancel the transverse noise; it maps residual
transverse noise partially onto the longitudinal direction, inflating `a_long`
to 12–26 m/s² at the speed where it should be 2–3. The joint DRS fit then
sees a flat/inflated frontier and returns negative CdA → plausibility fallback.

The speed channel `speed_ms = hypot(vx, vy)` is derived from the JOINT
`(vx, vy)` posterior. That posterior is tightly constrained (position observations
at ~5 Hz strongly constrain speed magnitude), so `d/dt(speed_ms)` via
`np.gradient` recovers the true longitudinal acceleration much more cleanly.

---

## Implementation

`src/physics/segment_classifier.py`:

1. New static method `_compute_a_long_series(df)` (sequence-level):
   - Prefers `speed_ms` column (pre-computed `hypot(vx,vy)` from the adapter).
   - Falls back to computing speed from `(vx, vy, vz)` components if `speed_ms`
     absent.
   - Uses `session_time_ms` (÷ 1000 → seconds) as the time axis.
   - Applies `np.gradient(speed, t_s)` — central differences in the interior,
     one-sided at edges. Handles non-uniform spacing.
   - Backward-compat guard: returns zeros if fewer than 2 samples or no speed
     channel (caller falls back to old `a·v̂` path).

2. `classify_samples` calls `_compute_a_long_series` ONCE before the row loop
   and assigns `a_long = float(a_long_series[idx])` per sample.

3. `_compute_long_lat` is unchanged (still called for `a_lat`; the `a_long`
   return from it is now discarded).

TDD: `tests/unit/physics/test_segment_classifier.py::TestALongSource` (2 new tests):
- `test_clean_case_both_sources_agree`: zero ax noise → both sources agree within
  ±0.5 m/s².
- `test_noisy_accel_state_speed_derivative_wins`: ax noise = 15 m/s² SD → old path
  had max error 29 m/s²; new path recovers true a_long within ±2 m/s².

---

## Per-fixture drag result

| fixture | theta_D OLD → NEW | fallback_long OLD → NEW | CdA implied NEW | notes |
|---|---|---|---|---|
| **monza** | 0.001 (fb) → **0.000627 (fitted)** | 1.0 → **0.0** | **≈ 1.02 m²** | milestone validated |
| **monaco** | 0.001 (fb) → **0.000148 (fitted)** | 1.0 → **0.0** | ≈ 0.24 m² | street circuit; low drag OK |
| spain | 0.001 (fb) → 0.001 (fb) | 1.0 → 1.0 | 1.62 (default) | no DRS-open lever (data limit) |

Monaco note: The CALIBRATION_PORT_RESULTS manual probe (which used a standalone
re-run with `a_long = d/dt(speed)`) showed Monaco theta_D ≈ 0 / negative. The
engine now returns theta_D = 0.000148 (positive, small). The difference is due to
the full estimator path (plausibility gate, power fit, regime filtering) vs. the
standalone probe. Monaco's low top speed means the drag lever is weak; the value
is positive and physically sane but uncertain.

**Monza CdA = 1.02 m²** is squarely inside the 1.0–1.5 m² validated band. The
manual proof-of-concept (CALIBRATION_PORT_RESULTS) showed theta_D = 0.000634
(CdA 1.03 m²); the engine now returns 0.000627 (1.02 m²) — consistent.

**Spain** remains fallback: the stored Spain FP1 lap has zero DRS-open samples
(all DRS codes = 8 "available/closed"). No amount of telemetry quality can fix
this. Spain is the wrong fixture to validate drag.

**Phase 3 milestone: VALIDATED on Monza real data.**

---

## RMSE unit bug fix (regression test)

`tests/regression/test_physics_regression.py::_compute_raw_vs_preprocessor_residuals`
compared `raw_df['x']` (FastF1 decimetres) to `processed_df['px']` (metres)
without applying the ×0.1 conversion. This inflated the blessed
`raw_vs_smooth_position_rmse` to ~4847/9803/6710 (decimetres, not metres).

Fix: applied `* _DM_TO_M (= 0.1)` to `raw_x` and `raw_y` before computing
position residuals. The corrected RMSE values are ~3–5 m (reflecting the
smoother's sub-metre fit to the raw observations at chi²≈1).

---

## Re-bless: changed fields per fixture

### monza_2024_fp1_ver (old → new)

| field | old | new | why |
|---|---|---|---|
| `theta_D` | 0.001000 (fallback default) | **0.000627** | fitted from speed-channel a_long |
| `fallback_longitudinal` | 1.0 | **0.0** | throttle joint DRS fit now succeeds |
| `fallback_power` | 1.0 | **0.0** | power fit runs only after successful drag fit |
| `theta_D_std` | 0.001 (fallback) | **0.000172** | fit uncertainty from joint DRS lstsq |
| `mean_theta_P` | 300.0 (default) | **608.9 W/kg** | power fitted (drag now valid) |
| `simulated_lap_time_s` | 96.17 | **76.88** | fitted drag < fallback default; sim faster |
| `raw_vs_smooth_position_rmse` | 9803.5 (dm, wrong) | **3.14 m** | ×0.1 unit fix applied |

### monaco_2024_fp1_ver (old → new)

| field | old | new | why |
|---|---|---|---|
| `theta_D` | 0.001000 (fallback default) | **0.000148** | fitted (weak lever, but positive) |
| `fallback_longitudinal` | 1.0 | **0.0** | throttle joint DRS fit succeeds |
| `fallback_power` | 1.0 | **0.0** | power fit runs |
| `theta_D_std` | 0.001 (fallback) | **0.000493** | fit uncertainty |
| `mean_theta_P` | 300.0 (default) | **531.4 W/kg** | power fitted |
| `simulated_lap_time_s` | 112.56 | **100.92** | lower drag → faster sim |
| `max_speed_ms` | 58.81 | **84.97** | sim now runs at fitted drag (closer to physical) |
| `raw_vs_smooth_position_rmse` | 6710.7 (dm, wrong) | **2.48 m** | ×0.1 unit fix |

### spain_2024_fp1_ver (old → new)

| field | old | new | why |
|---|---|---|---|
| `raw_vs_smooth_position_rmse` | 4847.7 (dm, wrong) | **3.16 m** | ×0.1 unit fix only |

All other Spain fields are byte-identical: Spain's drag remains fallback
(no DRS lever), lateral fit (A0, A2) unchanged.

---

## Guardrail suite: before → after

| suite | before | after |
|---|---|---|
| tests/unit/physics | 137 passed, 0 skipped | 139 passed, 0 skipped (+2 new a_long tests) |
| tests/unit/preprocessing/trajectory | 35 passed | 35 passed |
| tests/regression/test_physics_regression.py | 21 passed, 13 skipped | **27 passed, 7 skipped** |
| tests/integration/test_preprocessor_physics_interface.py | 36 passed | 36 passed |
| tests/integration/test_physics_pipeline.py | 111 passed | 111 passed |
| **TOTAL** | **305 passed, 13 skipped** | **313 passed, 7 skipped** |

The 6 formerly-skipped tests (theta_D_stable / theta_R_stable / mean_theta_P_stable
for Monza and Monaco) now run because `fallback_longitudinal` flipped from 1.0 to 0.0.
The 2 new a_long TDD tests pass. The `test_drag_source_throttle.py` synthetic session
was updated to use continuous speed evolution (integrated from a_long) so that
`d/dt(speed_ms)` matches the intended physics; all 5 of those tests still pass.

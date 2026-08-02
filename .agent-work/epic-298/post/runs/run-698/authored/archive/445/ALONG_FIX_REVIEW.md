# #445 a_long fix + drag re-validation -- Independent Code Review

**Reviewer:** Independent (fresh eyes, did not write the code)
**Date:** 2026-06-16
**Verdict: APPROVE-WITH-NITS** (no blockers, but Monaco drag call is a nit worth flagging loudly)

Test run: `313 passed, 7 skipped` (269 s). Green.

---

## Suite counts

| suite | result |
|---|---|
| tests/unit/physics | 139 passed, 0 skipped |
| tests/unit/preprocessing/trajectory | 35 passed, 0 skipped |
| tests/regression/test_physics_regression.py | 27 passed, 7 skipped |
| tests/integration/test_preprocessor_physics_interface.py | 36 passed, 0 skipped |
| tests/integration/test_physics_pipeline.py | 76 passed, 0 skipped |
| **TOTAL** | **313 passed, 7 skipped** |

Matches the claimed 305→313 (+8: 6 formerly-skipped + 2 new TDD tests).

---

## Findings

### 1. `_compute_a_long_series` -- PASS with docstring nit

**Correctness:** `np.gradient(speed, t_s)` correctly handles non-uniform
spacing via central differences in the interior and one-sided at the edges.
`speed_ms` column is preferred (pre-computed `hypot(vx,vy)` from adapter);
falls back to computing from `(vx, vy, vz)` if absent. Signing is correct:
decelerating speed decreases, gradient is negative. Interior samples verified
by `test_clean_case_both_sources_agree` (agree to 0.5 m/s^2 vs truth = 3.0).

**Duplicate/non-monotonic timestamps:** Fixtures checked:
- Monza: min gap = 6 ms, 0 duplicates
- Monaco: min gap = 1 ms, 0 duplicates
- Spain: min gap = 3 ms, 0 duplicates

No divide-by-zero risk on real data. No guard for duplicates is a latent issue
but not triggered today.

**Docstring is wrong (nit):** The docstring on `_compute_a_long_series` states
"the caller falls back to old `a·v̂` approximation instead." The code does NOT
do this. Line 62 is `a_long = float(a_long_series[idx])` unconditionally. When
the fallback returns zeros, **all samples get `a_longitudinal=0`** -- the drag
fit then sees no deceleration signal and falls back to default. This is harmless
on degenerate inputs (n<2 etc.) but the docstring falsely implies a graceful
per-sample fallback that does not exist.

---

### 2. Zeros-fallback safety -- CONDITIONAL PASS

**Verdict: safe for the current production path.**

The zeros path triggers only on: (a) fewer than 2 rows, (b) no speed column
AND no `vx/vy`, or (c) no `session_time_ms`. The adapter contract requires all
three of these (`session_time_ms` is a mandatory output per the interface tests).
No existing test exercises the zeros path and gets wrong `a_long`; all real-data
paths have `session_time_ms + speed_ms`.

**Latent risk:** If a caller ever passes a hand-built DataFrame without
`session_time_ms` (e.g., a future test or fast-path caller), they will silently
get `a_longitudinal=0` for all samples with no warning or error. The docstring
implies the old `a*v_hat` path would activate; it won't. A `warnings.warn`
or explicit comment "returns zeros, NOT a*v_hat" would be safer.

---

### 3. Monaco drag plausibility -- NONTRIVIAL CONCERN

**Verdict: Monaco drag fit is NOT trustworthy and should arguably stay fallback.**

Numbers from the fixture:
- `theta_D = 0.000148`, implied CdA = `0.000148 * 2 * 800 = 0.237 m^2`
- Real Monaco F1 high-downforce CdA: ~1.5--2.0 m^2 (DRS closed)
- Monaco CdA is **6--8x lower than physical expectation**
- `theta_D_std = 0.000493` -- **relative uncertainty = 3.3x** (SNR < 1)
- 1-sigma CdA range: [-0.55, 1.03] m^2 -- **includes negative values**
- DRS-open samples: 39 of 627 total (6.2%); speed lever: 8.3 m/s
  (DRS-closed max 79 m/s, DRS-open max 87 m/s)

The fit is statistically positive and the plausibility gate passes, but the
result has no physical grounding. Monaco's weak DRS lever (slow tunnel,
max 313 km/h vs Monza's 393 km/h) means there is insufficient
energy difference between open/closed regimes to resolve CdA. The REBLESS doc
acknowledges "low top speed / weak drag lever" but classifies this as "positive
and physically sane but uncertain." Uncertain is an understatement: the
1-sigma interval spans negative CdA to roughly the Monza value. The fit
reporting `fallback_longitudinal=0.0` is misleading; the parameter carries
essentially no information about Monaco's actual drag.

**Recommendation (non-blocking nit):** Extend the plausibility gate to also
reject fits where `theta_D_std / theta_D > threshold` (e.g., 2.0) or where
`theta_D_std > theta_D` (SNR < 1 is not meaningful). Monaco would then correctly
fall back. This does not need to block this PR, but should be tracked as a
follow-up issue.

---

### 4. Six formerly-skipped stability tests -- MIXED

Four of the six genuinely test regression stability:
- `test_theta_D_stable` for Monza and Monaco: fitted theta_D against blessed
  theta_D. GENUINE -- exercises the new code path.
- `test_mean_theta_P_stable` for Monza and Monaco: fitted power against blessed
  power. GENUINE -- power now runs only after successful drag fit.

Two pass **trivially**:
- `test_theta_R_stable` for Monza and Monaco: `theta_R = 0.5` (hardcoded
  default), `coast_samples = 0.0`, `theta_R_std = 1.0` (fallback). The skip
  condition checks `fallback_longitudinal` (drag), not whether theta_R itself
  was fitted. These tests are comparing 0.5 == 0.5, adding no regression
  coverage for rolling resistance. They should skip on
  `theta_R_std >= 1.0` (or `coast_samples == 0`), not on `fallback_longitudinal`.

---

### 5. Re-bless honesty -- PASS

Confirmed against actual blessed JSON:

| fixture | theta_D | fallback_long | fallback_power | lateral | RMSE |
|---|---|---|---|---|---|
| monza | 0.000627 (fitted) | 0.0 | 0.0 | still fallback (A0=30.0, A2=0.001) | 3.14 m |
| monaco | 0.000148 (fitted) | 0.0 | 0.0 | still fallback (A0=30.0, A2=0.001) | 2.48 m |
| spain | 0.001 (fallback) | 1.0 | 1.0 | fitted (A0=30.77, A2=0.00371) | 3.16 m |

No silent drift on lateral params for Monza/Monaco (A0/A2 byte-identical to
fallback defaults). Spain lateral unchanged. RMSE unit fix applied: 3--5 m
range is physically plausible for a smoother fitting 5 Hz GPS.

**Anomaly noted (pre-existing):** Monza and Spain `max_speed_ms` in
`blessed_params.json` are 329.1 m/s (1185 km/h) and 311.9 m/s (1123 km/h)
respectively. These are unphysical. Root cause: the track_profile for Monza
has its first segment spanning 0--240.6 m; the simulator starts at
`start_speed = 0`, then `v_next = sqrt(2 * (608 W/kg / ~0.001 m/s) * 240 m)` ->
supersonic. The backward pass and speed caps do not fully constrain this first
step. This is a **pre-existing simulator bug** (not introduced by this PR),
but it has been freshly blessed. The integration test
`test_max_simulated_speed_plausible` already emits a UserWarning for this
and does not fail, so it is documented but not blocked. Lap time (76.88 s)
is internally consistent despite the speed anomaly (the remaining segments
dominate the integral). Still, blessing a 1185 km/h value is misleading.

---

### 6. RMSE unit fix -- CORRECT

`_DM_TO_M = 0.1` applied to `raw_df['x']` and `raw_df['y']` before computing
position residuals. Blessed values of 3.14/2.48/3.16 m are consistent with
sub-metre smoother fit to 5 Hz GPS (chi^2 ~ 1). Confirmed: old values of
4847/9803/6710 were in decimetres, 10x inflated.

---

### 7. TDD tests -- GENUINE, not tautological

`test_clean_case_both_sources_agree`: zero ax noise, checks interior samples
(correctly excludes edges where np.gradient uses one-sided differences).
Tests actual agreement within 0.5 m/s^2 against truth = 3.0. GENUINE.

`test_noisy_accel_state_speed_derivative_wins`: ax noise = 15 m/s^2 SD,
verifies max error < 2.0 m/s^2 for the new path. The OLD path (a*v_hat on
the noisy state) would have max error ~29 m/s^2 on the same data. GENUINE --
distinguishes old behavior from new.

---

## Explicit calls

**(a) Zeros-fallback safety:** SAFE for the current production path. The
adapter contract guarantees `session_time_ms` and `speed_ms`, so the fallback
is never reached on real data. The docstring is wrong and should be corrected
to say "returns zeros -- a_longitudinal will be 0, not the old a*v_hat." This
is a non-blocking documentation nit.

**(b) Monaco drag fit trustworthy?** NO. CdA = 0.24 m^2 is 6--8x below the
physical Monaco expectation. SNR < 1 (theta_D_std = 3.3x theta_D). The fit
is indistinguishable from zero within 1 sigma. Monaco DRS lever is too weak
to constrain drag. The fit happens to be positive and pass the plausibility
gate, but it should not be treated as validated. The document's framing
("positive and physically sane but uncertain") understates the problem.
Recommend a follow-up issue to add SNR gate (`theta_D_std / theta_D > 2.0`
-> fallback). The Monza fit (CdA = 1.02 m^2, theta_D_std/theta_D = 0.27)
is genuinely validated; Monaco is not.

---

## Non-blocking nit list

1. **Docstring wrong:** `_compute_a_long_series` says "caller falls back to
   old `a*v_hat`" -- it does not. Fix to "returns zeros; a_longitudinal will
   be 0 for all samples."
2. **Monaco drag should fallback:** Add SNR gate to longitudinal fit plausibility
   check. Track as issue.
3. **theta_R_stable skip condition wrong:** Use `theta_R_std >= 1.0` (or
   `coast_samples == 0`) instead of `fallback_longitudinal`. The current skip
   misses that theta_R is the default value, not a fitted one.
4. **Blessed max_speed_ms anomaly:** 329/312 m/s for Monza/Spain is a
   pre-existing simulator first-segment bug now freshly locked in. Track as
   issue for `physics_simulator._forward_pass` initialization guard.

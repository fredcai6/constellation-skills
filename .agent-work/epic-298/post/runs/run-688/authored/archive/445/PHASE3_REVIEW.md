# Phase 3 Code Review — Drag-Source Swap (#445, D1)

**Reviewer:** Independent (fresh eyes, did not write this code)
**Date:** 2026-06-16
**Verdict:** APPROVE-WITH-NITS

All 210 physics tests pass (13 skipped), fixtures are byte-identical (git status clean on
`tests/fixtures/physics/regression/`), no re-bless occurred.

---

## Verdict Summary

The drag-source swap is mechanically correct: the physics is right, the DRS-decode bug
is genuine and the fix is correct, the fallback chain is safe, and the synthetic tests
genuinely validate the recovery. The two nits below are both non-blocking. The larger
concern — no real-data validation because all three fixtures are on fallback — is
accurately documented and is a known sequencing gap, not a Phase 3 defect.

---

## Assessment per scrutiny axis

### (a) Fit correctness — PASS

`fit_drag_throttle` correctly ports `drs_joint_fit.fit_drs_joint` with two deliberate
improvements over the reference:

1. The production code adds `len(v_open) < 1` as an explicit condition (line 214 in
   `longitudinal_fit.py`), which the reference implicitly relied on. This is strictly
   more conservative and correct.
2. The production code checks `len(samples) < min_samples_per_regime` BEFORE computing
   frontier bins, so the internal `< 5 total bins` gate is the only remaining None path
   from the inner call — the outer estimator's disambiguation is correct.

Units check: `a = P/(m·v) − 0.5·ρ·CdA·v²/m` → `theta_D = CdA/(2·m)` with `m=MASS_KG=808`.
The design matrix columns are `[1/(MASS_KG·v), −0.5·ρ·v²/MASS_KG·1{closed}, −0.5·ρ·v²/MASS_KG·1{open}]`,
which recovers `[P, CdA_closed, CdA_open]`. Converting `theta_D = CdA_closed * scale` where
`scale = 1/(2*MASS_KG)` and propagating variance: `theta_D_std = sqrt(cov[1,1]) * scale`. All correct.

The covariance is the honest `s²·(XᵀX)⁻¹` using `pinv` and DOF-correct `s²`. The condition
number is computed and stored (useful for monitoring degeneracy).

The plausibility gate (negative theta_D → fallback; too-large → fallback; non-finite std →
fallback) is in the estimator (not the fit), which is the correct separation of concerns.

### (b) DRS-decode fix — PASS

Old code (`control_alignment.py` commit 1938453):
```python
drs = bool(drs_val) if not np.isnan(drs_val) else False
```
`bool(8)` is True, so code 8 ("DRS available/closed") was reported as open. This is
confirmed wrong: FastF1 DRS codes are 0/1/8 = off/available-closed, 10/12/14 = active-open.

New code:
```python
return int(round(value)) in (10, 12, 14)
```
This is correct. The test `test_drs_decode_open_vs_closed` explicitly exercises all 6
codes (0, 1, 8, 10, 12, 14) and asserts the correct True/False split.

Impact of the old bug: every sample at code 8 (the most common non-open state on a DRS-eligible
straight) was placed in the "DRS-open" bin of the joint fit, poisoning the P/CdA_closed split.
This would have produced a badly mis-identified CdA_closed on any session where the car
spends time in DRS-available-but-closed state (which is essentially every session post-2011).
The fix is correct and important.

The `_drs_is_open` static method handles NaN and non-numeric inputs gracefully. The nearest-index
strategy for DRS (vs kernel interpolation for throttle/brake) is consistent with the pre-existing
code — a design choice not introduced in Phase 3.

No other DRS consumers exist in `src/physics/` beyond `ControlAlignment`. No other call sites
affected.

### (c) All-seasons fallback safety — PASS (with documentation gap noted)

No era-aware selector exists in the current code. For pre-2014 sessions:
- `fit_drag_throttle` is called with whatever data is present.
- If there is no DRS (≤2010) there will be no DRS-open bins → `len(v_open) < 1` → returns None.
- If there is KERS+DRS (2011–2013) there may be open bins, but the coast regime is
  MGU-K-free so the returned CdA could actually be usable (KERS harvested under braking, not
  coasting — but Phase 3 currently DISCARDS coast drag regardless of era).

For the 2011–2013 window: if a pre-2014 session has both DRS and a few open bins (e.g., driver
briefly uses DRS) the fit fires and may return a plausible theta_D. If the data is clean that's
acceptable; if not, the plausibility gate catches it.

The gap is: the coast drag path (`fit_drag_rolling`) is never used as a theta_D source even for
2011–2013 where it would be valid. `ALL_SEASONS_AND_VALIDATION.md` documents this correctly.
The fallback (default `theta_D=0.001`) is conservative and safe — it won't produce silently wrong
drag, just reduced accuracy.

Hook point for the era selector: `parameter_estimator.py` lines 100–112, where `throttle_fit`
is called. An era switch here would call `fit_drag_rolling` for theta_D (not theta_R) when year ≤ 2013.

### (d) Validation gap legitimacy — LEGITIMATE, WELL-DOCUMENTED

The three blessed fixtures (Spain/Monza/Monaco 2024 FP1) all remain on fallback for a legitimate
reason: their `processed_telemetry` contains uncalibrated kinematics (speeds to 529 km/h,
|ax| to 236 m/s²). These are not representative of real F1 data; they are fixture artifacts from
when the preprocessing smoother was not yet calibrated. The p90 frontier bins in the joint fit
latch onto these noise spikes and drive CdA negative — correctly caught by the plausibility gate.

`PHASE3_FIXTURE_REBLESS_PROPOSAL.md` documents this clearly. The integration test
`test_max_simulated_speed_plausible` also shows the consequence: Monza simulates at 1185 km/h
(with the fallback theta_D=0.001 and fallback power), which the test catches and warns about
rather than failing.

The chain is: bad kinematics → bad throttle fit → negative CdA → plausibility gate fires →
fallback → tests pass. The fallback is not masking a bug in the fit itself; the synthetic tests
prove the fit works on clean data.

---

## Findings

### Finding 1 (NITS — longitudinal_fit.py:61-63)
**Severity:** Low (documentation / future confusion)
**Location:** `src/physics/longitudinal_fit.py`, `DragThrottleFit` dataclass, field
`drag_rolling_covariance` (line ~61-63)

**What:** The `DragThrottleFit` dataclass has a field `drag_rolling_covariance` documented
as "2x2 covariance for [theta_D, theta_R] in the engine's convention. Only the theta_D
variance comes from this fit; the theta_R block is filled by the caller."

**Problem:** `fit_drag_throttle` never populates this field — it is `None` on every returned
`DragThrottleFit`. The estimator never reads it (it builds `drag_rolling_cov` from
`np.diag([theta_D_std**2, theta_R_std**2])` independently). The field is therefore dead weight
with a misleading docstring claiming the caller will fill it — but no caller does.

**Fix:** Either (a) remove the field from `DragThrottleFit` entirely (the estimator assembles
the block-diagonal itself, which is cleaner), or (b) have `fit_drag_throttle` populate it with
`np.diag([theta_D_var, 0.0])` (leaving theta_R as 0 as a sentinel for "caller fills this").
Option (a) is cleaner.

---

### Finding 2 (NITS — parameter_estimator.py:108-111)
**Severity:** Low (misleading metric name)
**Location:** `src/physics/parameter_estimator.py`, lines 106–112

**What:** When `throttle_fit is None` because the frontier binning returned too few bins (e.g.,
insufficient speed spread, even with enough raw samples), the fallback reason is recorded as
`"no_drs_lever"`. But this can also fire when the car has no high-speed *range* rather than
no DRS-open lever per se (e.g. a very slow circuit with all speeds below 50 m/s even with
DRS-open samples existing). The message would mislead debugging.

**Fix:** Tighten the disambiguation: distinguish `"no_drs_open_bins"` (v_open bins = 0) from
`"insufficient_total_bins"` (v_closed + v_open < 5 with v_open >= 1). This requires either
surfacing the inner None reason from `fit_drag_throttle` (e.g. returning an enum) or doing the
bin-count check in the estimator before calling.

---

### Finding 3 (OBSERVATION, not a defect — test coverage)
**Location:** `tests/unit/physics/test_longitudinal_fit.py`

`test_fit_drag_throttle_uses_only_high_throttle` (line 102) uses `rel=0.08` tolerance — the
widest in the test file. This is because the injected low-throttle samples add noise, and the
p90 frontier may bias slightly. This is acceptable but worth noting: the high-throttle filter
uses `>= high_throttle_threshold` (0.9 in [0,1] units), while the synthetic test injects
throttle_value=0.2 (already excluded) and throttle_value=1.0 (the clean data). The test does
confirm the filter works, but it does not stress-test boundary samples (e.g. throttle_value=0.89
vs 0.90). Not a blocking issue.

---

### Finding 4 (OBSERVATION — test coverage gap, not blocking)
**Location:** Tests generally

No test directly validates that `theta_R` flows from the coast fit when the throttle fit
succeeds AND the coast fit is plausible. `test_theta_R_still_comes_from_coast` does this with
THETA_R_COAST=1.5 m/s², which is in the plausible range (≤5.0) and passes the `fit_R_std < fit_R`
check with clean synthetic data. This is adequate but tests a single (well-behaved) coast. The
implausible-coast path is tested separately in `test_plausibility_fallback.py:test_implausible_coast_theta_R_does_not_fail_longitudinal`.
Coverage is sufficient.

---

### Finding 5 (OBSERVATION — integration test warning, not new)
**Location:** `tests/integration/test_physics_pipeline.py`

The integration tests emit "Sim max speed 1185 km/h (longitudinal fit unreliable)" for Monza.
This is a pre-existing fixture quality issue (uncalibrated kinematics → fallback theta_D=0.001 →
power fit with negligible drag → infinite-acceleration run). The test correctly converts this to
a warning-and-return rather than a failure. This is not introduced by Phase 3 — it was the
behavior before as well (the coast drag was also failing plausibility on these fixtures).

---

## Test rigor assessment

The synthetic tests genuinely validate the drag recovery:
- `test_fit_drag_throttle_recovers_known_cda` uses zero noise and recovers CdA_closed within 3%
  and power within 5%. The known-answer fixture is constructed identically to the model the fit
  inverts, so this is a tight test.
- `test_fit_drag_throttle_theta_D_relationship` verifies the algebraic identity
  `theta_D = cda_closed / (2*MASS_KG)` to 9 decimal places — correct.
- `test_theta_D_comes_from_throttle_not_coast` in `test_drag_source_throttle.py` is the most
  important test: it builds a session where coast drag is inflated 6× by synthetic regen, and
  confirms `theta_D` matches the clean throttle truth (within 10%) and is far below the inflated
  coast value. This is the D1 hypothesis tested end-to-end.
- `test_theta_R_still_comes_from_coast` confirms the split routing.
- Covariance routing test (`test_throttle_theta_D_uncertainty_feeds_covariance`) verifies the
  `drag_rolling_covariance[0,0] == theta_D_std**2` identity — correct.
- None-return tests (no DRS lever, insufficient samples, implausible negative drag) are all
  present and pass.

No tautologies detected. The tests are structurally independent of the implementation (they
build samples from the physics model, not from the fit output).

---

## What Phase 3 does NOT validate

1. The joint fit on REAL calibrated telemetry (blocked on calibrated smoother — documented).
2. The era-aware selector for ≤2013 coast drag as theta_D (documented as future work in
   `ALL_SEASONS_AND_VALIDATION.md`; current behavior is safe fallback, not silent error).
3. Sensitivity to the `high_throttle_threshold=0.9` gate (partially validated by Finding 3 above;
   not blocking).

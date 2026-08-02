# Phase 5 Review — Braking Frontier + Friction Circle (#445)
Reviewer: independent code reviewer (claude-sonnet-4-6), 2026-06-16

## Verdict: APPROVE-WITH-NITS

**Test run:** `py -m pytest tests/unit/physics tests/regression/test_physics_regression.py tests/integration/test_physics_pipeline.py -q`
Result: **293 passed, 10 skipped** — matches the claim exactly. No regressions.

---

## (a) Constant-mode byte-identical preservation — CONFIRMED

When `parameters.braking is None`, `_compute_braking_decel` falls through to the
pre-Phase-5 block unchanged: `decel = config.max_braking_ms2` with friction circle
gated on `config.apply_braking_friction` (defaults `False`). The branch is
structurally identical to the pre-Phase-5 code; `None` is the default on
`PhysicsParameterSet.braking`, so all code paths that don't explicitly set
`braking=` continue to receive `braking=None` and hit the constant path.

All three blessed fixtures (Spain/Monza/Monaco) report `braking_source="constant"` and
their `simulated_lap_time_s`/`max_speed_ms` fields are unchanged by Phase 5. The
`braking_source` key is correctly NOT included in `_extract_param_dict()`, so fixture
comparison is unaffected. The git diff of the JSON files between the SNR-gate bless
(the commit state) and the working tree shows NO new Phase-5-originated changes to the
blessed JSONs (the diffs visible are from earlier phases already committed).

`_sample_parameters` likewise: the braking block is guarded by
`if parameters.braking is not None`, so zero covariance perturbation is added for the
constant path.

**Call: constant-mode preservation is CORRECT and COMPLETE.**

---

## (b) Friction-circle physics correctness — FUNCTIONALLY CORRECT WITH A DESIGN NOTE

The frontier-mode friction circle formula:

```python
a_lat_req = speed ** 2 * abs(curvature)
decel = float(np.sqrt(max(0.0, decel ** 2 - a_lat_req ** 2)))
```

- `a_lat_req` is centripetal acceleration demand (v²·|κ|), which in a quasi-static
  point-mass sim IS the actual lateral force the car exerts. This is the standard
  formula for the friction circle.
- Dimensionally consistent: m/s² vs m/s² under the sqrt.
- Corner detection uses `is_corner = abs(curvature) >= simulator_curvature_threshold`
  — the same threshold as `_compute_speed_caps`, so friction circle applies exactly
  where speed caps apply. No double-application: speed caps constrain the MAXIMUM
  speed through corners (forward pass + final min), while the friction circle
  constrains how fast the car CAN DECELERATE approaching a corner (backward pass).
  These are complementary constraints, not the same thing applied twice.

**Design note (not a bug):** the frontier mode and the constant mode use DIFFERENT
friction-circle reference capacities. Constant mode: `decel *= sqrt(1 - (a_lat/a_lat_max)^2)`
with `a_lat_max` from the lateral grip envelope. Frontier mode: uses `a_brake(v)` as
the total capacity. These are physically inconsistent between modes. The frontier
formula is the more standard form (Kamm circle); the constant-mode formula is a
scaled-fraction variant. Since the two modes are mutually exclusive (gated by
`parameters.braking is not None`) this inconsistency has no practical impact, but
it is a code-quality debt if the constant mode's friction circle is ever turned on
in production.

**Call: friction-circle physics is CORRECT for the quasi-static sim architecture.
No double-application. Formula is standard. Inconsistency with constant mode is
a design note, not a bug.**

---

## Numbered Findings

### Finding 1 — NITS: Braking SNR gate has no estimator-level test

The drag SNR gate has two estimator-level tests in `test_plausibility_fallback.py`:
`test_high_relative_sigma_triggers_fallback` and `test_low_relative_sigma_keeps_fit`,
both asserting on `fit_quality_metrics` to confirm the gate actually routes to fallback
or not. The braking SNR gate has no equivalent: `test_low_snr_scenario_has_large_relative_sigma`
only asserts `rel_sigma >= 0.0` (tautological) and even `pytest.skip`s when the fit
returns `None`. There is no test that calls `estimate_parameters` with high-sigma
braking data and asserts `params.braking is None` and
`fit_quality_metrics["braking_source"] == "constant"`.

**Severity: NIT.** The gate logic is present and correct in the code; the path is
exercised implicitly by all three fixtures falling back. But the test is weaker
than the drag-gate test analogue. Recommend adding a direct estimator-level test
mirroring `test_high_relative_sigma_triggers_fallback`.

### Finding 2 — NIT: b_b MC lower bound is physically unmotivated

In `_sample_parameters`, `b_b` is clipped to `[-0.1, 1.0]`. The value `-0.1` is
arbitrary: at `v = 14.8 m/s`, `b_b = -0.1` would cancel `a_b = 22 m/s²` entirely,
leaving zero braking at all speeds > 14.8 m/s. The `a_brake()` helper clamps to
zero, so no negative deceleration escapes, but the effective braking frontier
collapses. This is prevented only by the `a_b` being clipped to [0, max_braking_ms2],
which partially rescues the formula. A physically motivated lower bound would be
`max(-a_b/v_hi^2, 0)` (preserving non-negative braking at the highest observed speed)
or simply `b_b >= 0` (aero braking cannot reduce with speed). With typical b_b ~ 0.002
and real covariance σ_b_b << 0.1, the clip rarely fires — this is a latent issue not
a current defect.

**Severity: NIT.**

### Finding 3 — NOTE: `test_lap_time_identical_when_braking_none` does not verify pre-Phase-5 byte-identity

The test runs two calls with the same params — trivially deterministic. It does not
compare output to a pre-Phase-5 baseline (e.g., a known lap time from a golden run).
Byte-identity is instead verified indirectly via the regression test's fixture comparison.
Since the regression fixtures are the authoritative check and they pass, this is
acceptable — but the test name overclaims what it actually proves.

**Severity: NOTE (documentation only).**

### Finding 4 — CONFIRMED CORRECT: Threshold calibration

`min_pts_per_bin=8, min_bins=4` requires ~32+ samples in a useful speed range.
Spain diagnostic (`min_pts_per_bin=5` relaxed) yields `A_b=35.5, B_b=-0.0023` with
rel-σ=47% — physically questionable (negative B_b from narrow lever). The default
threshold correctly rejects this and all three single-lap fixtures. The multi-season
consolidation (many laps) passes easily. Threshold calibration is appropriate and
matches the consolidation's extrapolation-limited finding.

### Finding 5 — CONFIRMED CORRECT: a_b=0 zero-guard

`rel_sigma = frontier.a_b_std / max(abs(frontier.a_b), 1e-12)` — when `a_b` is
near zero, this produces a very large rel_sigma that correctly triggers the gate,
returning `None`. No ZeroDivisionError. This mirrors the drag gate's guard exactly.

### Finding 6 — CONFIRMED CORRECT: Joint MC draw from braking covariance

`_sample_parameters` draws `(a_b, b_b)` jointly from the 2×2 covariance when
`parameters.braking is not None`, with a `1e-30` regularisation for numerical
stability. `perturbed_braking = None` when `parameters.braking is None` — no
spurious variance added. The `test_braking_covariance_is_sampled_jointly` test
verifies that 50 draws produce varying `a_b` values (std > 0.1), confirming the
joint draw is active.

---

## Summary of two explicit calls

| Question | Answer |
|---|---|
| Constant-mode byte-identical preservation | YES — `braking=None` path is untouched, regression fixtures confirm no Phase-5-originated field changes. |
| Friction-circle physics | CORRECT — `a_lat_req = v²·|κ|` is the right quantity for quasi-static sim; formula is standard Kamm circle; no double-application. Design note: frontier and constant modes use inconsistent friction-circle reference capacities (harmless given mutual exclusivity). |

## Test quality assessment

20 braking-fit + 14 braking-simulator tests. Generally solid:
- Known-answer recovery with tolerance (<20% A_b, B_b) — acceptable given p95 frontier noise.
- Covariance PSD/finite/std-consistency — thorough.
- Insufficient data paths — 4 variants, all meaningful.
- Friction-circle formula test (`test_friction_circle_formula`) — verifies exact numerical identity to the formula, not just direction. Good.
- MC variance contribution — verified with large covariance.
- Zero-covariance → zero variance path — verified.
- Constant-mode config-exact test — good.

Weaknesses: SNR gate test is tautological (Finding 1); byte-identity test is trivially deterministic (Finding 3).

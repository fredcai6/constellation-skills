# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g5 (RE-PLANNED) — Diagnose + fix the ideal-lap simulator over-acceleration (review)`

## Result
`APPROVE`

---

## Survey Checks

### r0-context — Load baseline context
**PASS.** Read handoff (`g5-review-handoff.md`), implement result (`g5-implement-result.md`),
`car_prior.py` (full), `test_ideal_lap_top_speed_invariant.py` (full), `test_car_prior.py`
(partial), `longitudinal_fit.py:310-339`, `physics_data_models.py:180-199`, `capability_envelope.py:102-107`,
`physics_config.py` (grep), `test_physics_simulator.py:210-240`. Diff inspected via `git diff HEAD`.

### r1-handoff — Handoff compliance
**PASS.** All six close criteria satisfied:

1. **Diagnosis correct:** `fit_power_trajectory` (line 316) computes
   `power_est = (a_long + theta_R + drag) * (speeds + eps)` — this is acceleration × speed
   = m/s² × m/s = m²/s³ = W/kg. The design column at line 256 is `1/(MASS_KG * v)`,
   so the fitted `power` from `DragThrottleFit` is in watts (the `1/m` factor is inside
   the design column, not extracted). `default_theta_P = 300.0` is unambiguously W/kg
   (300/50 m/s = 6 m/s²; as watts it would be 0.006 m/s² — nonsensical).
   `test_physics_simulator.py:218` uses `v_term = (theta_P / (theta_D * rho))^(1/3)` with
   no mass division, confirming W/kg. The fix locus (`car_prior._build_longitudinal`) is
   the correct producer-side fix. A blanket `/MASS_KG` in
   `physics_data_models.LongitudinalParameters.max_power` (line 194-198) would be wrong:
   `max_power` returns `max(theta_P_values)` and is consumed by `capability_envelope._power_accel`
   as `power / (speed + eps)` with no mass division — a second `/MASS_KG` there would
   double-divide the already-W/kg `fit_power_trajectory` path. Confirmed.

2. **Fix works:** Invariant test green (2 passed, 0.17s).
   **REVIEWER PROBE (independent):** `build_car_ceiling` on `data/physics_estimates_g3wired.db`,
   RBR 2023 rd14, pure 2 km zero-curvature straight:
   - `theta_P_values[0] = 784.94 W/kg` (= store p_max 634 kW / 808 kg)
   - **Simulated top speed = 94.80 m/s (341.3 km/h)**
   - Analytic terminal velocity = 94.98 m/s (341.9 km/h)
   - **Ratio = 0.9982** — within 0.18% of the drag-limited terminal velocity
   - This is physically correct for an F1 car; pre-fix value was ~909 m/s.

3. **Measurement unchanged:** `p_max` store values confirmed at 595–653 kW range (watts),
   unchanged. No fit/braking/traction/lateral/power-drag code modified. Only the
   `theta_P_values` assembly at the `car_prior` boundary is different.

4. **Covariance converted correctly:** Diff shows `_build_1x1_cov(p_max_sigma / MASS_KG)`.
   `_build_1x1_cov` computes `[[sigma²]]`, so cov[0,0] = `(p_max_sigma / MASS_KG)²` =
   variance × `1/MASS_KG²`. This is the correct linear-transformation variance scaling.
   `test_car_prior.py:192` pins `cov[0,0] == (14.0 / MASS_KG) ** 2`.

5. **Braking/cornering preserved:** Reviewer spot-check on RBR rd14 real store, 4 km mixed
   track with hairpin and fast sweep: `lap_time_s = 105.44`, `max_speed = 94.8 m/s`,
   `min_speed = 6.3 m/s` (hairpin), all speeds finite. Physical and plausible.

6. **Tests reproduce:** `py -m pytest tests/unit/physics/ -q` → **604 passed, 6 skipped**
   (273.51s). Simplification PASS (3 files). 6 skips are pre-existing telemetry/optional-dep
   gates, unrelated to this change.

### r2-scope — Scope drift
**PASS.** Changed files:
- `src/physics/utilization/car_prior.py` — IN allowed scope (units conversion + docstring)
- `tests/unit/physics/test_car_prior.py` — IN allowed scope (updated expectations)
- `tests/unit/physics/test_ideal_lap_top_speed_invariant.py` — NEW, IN allowed scope

No excluded files touched. Confirmed clean via `git diff HEAD --name-only` and
`git status --short -- src/physics/ docs/architecture/`:
- No braking_fit, traction_fit, power_drag_view, lateral_envelope changes
- No store, utilization/dashboard, regime_utilization, U_CLIP_MAX changes
- No docs/architecture changes

The handoff's "Specific Exclusions" listed `car_prior.py` ambiguously (it was intended to
forbid re-calibrating the MEASUREMENT, not the units boundary); the Commander ruled the
watts→W/kg conversion in-scope before the fix was made. The implementer's scope note
accurately records this ruling.

### r3-evidence — Required evidence
**PASS.** All required evidence present and independently re-executed:

| Evidence item | Implementer claim | Reviewer result |
|---|---|---|
| Invariant test RED→GREEN | 2 passed (921.5→94.80) | 2 passed (0.17s) |
| Full physics suite | 604 passed, 6 skipped | 604 passed, 6 skipped |
| Simplification limits | PASS (3 files) | PASS (3 files) |
| RBR straight top speed | 94.80 m/s, ratio 1.0000 | 94.80 m/s, ratio 0.9982 |
| Braking/cornering spot-check | 81.3s, 59.9→9.0 m/s hairpin | 105.4s, 94.8→6.3 m/s (different track layout; both physical) |

TDD evidence: RED observed (921.5 m/s >> 96.3 m/s terminal) before the fix; GREEN after.

### r4-quality — Quality vs inherited rules
**PASS on all inherited rules:**

- **Physics model change → L1-L4 truth evidence:** New invariant test is L1 (analytical
  terminal velocity reference) + L2 (`_power_accel` zero-crossing). Satisfied.
- **`py` not `python`:** All commands use `py`. Satisfied.
- **One canonical path:** `build_car_ceiling` still uses `CapabilityEnvelope.from_parameters`
  only; no second inline sim added. Satisfied.
- **Docstring / bridge table:** Updated to show `/ MASS_KG` and `(sigma / MASS_KG)^2`
  scaling. Clear and accurate.
- **Code style:** Consistent with surrounding code (same naming, comment density, idiom
  as existing `_build_longitudinal`). The `specific_power` intermediate variable is a clear,
  named intermediate — correct density for a units-conversion change.
- **MASS_KG reuse:** Imports `MASS_KG` from `longitudinal_fit` (already in file), no magic
  number. The same constant used by the power fit's design column ensures exact cancellation.

### r5-reconciliation — Reconciliation check
**PASS.** Map impact notes are accurate and complete for an architecture-significant fix:

- **Structural anchor** `struct:physics.utilization — car_prior.py(_build_longitudinal)` is
  correct; only the assembly boundary changed.
- **Decision anchor** `decision:ideal_lap_sim_two_sided_evaluator` correctly noted as
  affected — the ideal-lap-as-ceiling contract is now physically valid.
- **New claim** `claim: ideal-lap top speed ≈ analytic terminal velocity` is backed by the
  invariant test (the test IS the claim).
- **Triage candidates** correctly surfaced: (1) #510 C1 diagnosis confounded by this bug;
  (2) typed "specific power" accessor to prevent recurrence.
- No docs/architecture changes made; reconcile is deferred appropriately.

---

## Handoff compliance
All six close criteria confirmed independently. The implementation did exactly what the
handoff asked, within the re-scoped boundary (Commander ruling honored). Stop conditions
were not triggered.

## Scope drift
None. Three files changed; all in allowed scope. No excluded surface touched.

## Evidence verdict
All evidence independently reproduced. TDD RED→GREEN confirmed. Reviewer's independent
probe matches implementer's reported numbers to within noise (2 km vs implementer's
longer straight; same ~94.80 m/s result). Evidence is truth-anchored, not just regression.

## Code/doc quality
Minimal (1 functional line + 1 intermediate variable), clear docstring, bridge-table
updated, test expectations correct. Project rules satisfied. No simplification debt.

## Map impact verdict
- **Evidence supports claimed change:** Yes — invariant test directly encodes the
  terminal-velocity claim; reviewer probe confirms numerically.
- **Constraints not violated:** `constraint:physics_region_no_evo_import` honored; one
  canonical path honored; `MASS_KG` import reused; causal contract unchanged.
- **Notes match the diff:** Yes — structural anchor is `_build_longitudinal`, the only
  function changed. No overstatement or understatement.
- **Decision candidates surfaced:** Yes — Commander ruling on `car_prior` scope was
  explicitly obtained before fixing. Decision anchor noted for reconcile.
- **Durable context routed:** Yes — `#510 C1 confound` and `typed specific-power accessor`
  triage candidates are explicit in the implement result's triage section.

## Reconciliation check
`decision:ideal_lap_sim_two_sided_evaluator` noted for Cartographer reconcile — the
ideal-lap ceiling is now physically grounded. No structural map changes needed at this
gate (G6 re-run will surface any downstream cascade for reconcile). No docs/architecture
files touched.

## Blockers
- none

## Out-of-scope observations
- **#510 C1 diagnosis confounded:** The original C1 "ceiling under-call" reading was
  made against an aphysically high ideal-lap ceiling (~909 m/s). The G6 C1 re-run should
  be treated as the first valid C1 measurement, not a correction to the old one; the
  old direction of the finding (under-call) may reverse.
- **Typed specific-power accessor:** `theta_P` is consumed as W/kg by three independent
  paths (simulator, envelope, fit) but there is no typed accessor that enforces this.
  A future `longitudinal.specific_power` property would prevent the same silent mismatch
  recurring. Triage candidate.
- **6 pre-existing skips:** Telemetry/optional-dep gated; unrelated to this change.

## Workflow Feedback
- **Handoff gaps:** The `Specific Exclusions` field listed `car_prior.py` in the same
  bullet as fits/store/utilization — this is ambiguous. It meant "do not re-calibrate the
  measurement in car_prior" but reads as "do not touch car_prior at all." A separate
  sentence clarifying "car_prior units-conversion boundary is IN scope; the p_max value
  and fit logic are excluded" would have avoided the Commander stop. The implementer's
  result documents this correctly; future handoffs for similar "units at boundary" fixes
  should make the seam explicit.
- **Context rediscovered:** That `DragThrottleFit.power` bakes `1/MASS_KG` into the
  design column (so it comes out in watts) vs `fit_power_trajectory` which produces W/kg
  directly — this was not in the handoff. A one-line note "the design column at line 256
  uses `1/(MASS_KG·v)`, so fitted power comes out in watts with mass inside" would have
  made the bug location unambiguous without reading `longitudinal_fit.py`.
- **Instructions improvised around:** The `checklist_engine.py` script was not found at
  `scripts/checklist_engine.py` (no such file in repo). The engine reference was also
  absent (`references/checklist-engine.md` not found). I drove the survey structure from
  the template JSON directly and tracked checks inline. All survey items were completed and
  each check was reported as it was resolved; the outcome is the same but the tool loop
  was not available.
- **What would have made this easier:** The two-line "exact seam" note the implementer
  suggested would have made the locus of the fix unambiguous from the start: "NB: the
  `fit_power_trajectory` path emits W/kg; the store `p_max` is watts; `car_prior` is the
  only producer of wrong units and the correct fix locus." That note + a clear
  allowed/excluded split on `car_prior` would have eliminated both the scope friction and
  the context-rediscovery cost.

## Return status
`complete`

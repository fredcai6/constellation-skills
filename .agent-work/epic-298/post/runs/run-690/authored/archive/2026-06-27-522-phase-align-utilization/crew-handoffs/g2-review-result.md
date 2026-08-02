# Review Result — G2 Lateral Units Fix, Option A Rework (#522)

## Assigned Gate
`g2-review (REWORK review) — #522 G2 Lateral Units Fix v2 / Option A`

## Result
`APPROVE`

---

## Handoff compliance

All four close criteria satisfied:

**1. Diff scope** — `git diff --name-only` returns exactly `src/physics/utilization/car_prior.py` + `tests/unit/physics/test_car_prior.py`. All explicitly excluded consumer/schema files (`physics_data_models.py`, `physics_simulator.py`, `capability_envelope.py`, `lateral_view.py`, `regime_utilization.py`) produce empty diffs — byte-identical to baseline. PASS.

**2. Conversion math correct and exact** — `A0_param = A0_g * G` (line 495); `A2_param = A2_g * G / air_density` (line 496). Exactness verified independently: `A2_param * rho = 0.00313920 == A2_g * G = 0.00313920` (float-exact because `*(G/rho)*rho == *G` with the same `rho`). Jacobian `J = diag(G, G/air_density)` applied via `jac @ lat_cov @ jac.T` at line 505, which is AFTER the blob/diagonal choice — single transform point covers BOTH the blob path (lines 498–501) AND the diagonal-σ path (lines 502–503). PASS.

**3. Default fallback physical** — the `else`-branch (lines 506–514) assigns `A0_param = cfg.default_A0`, `A2_param = cfg.default_A2` with NO Jacobian multiplication — `s0`/`s2` are defined only in the if-branch scope context but only multiplied in lines 495–496 (the store-pooled branch). `test_no_lateral_data_fallback_is_physical` asserts `lat.A0 == 30.0` (unconverted), `lat.A2 == 0.001` (unconverted), fallback floor `~ 3.06 g` ∈ [2, 6]. PASS.

**4. Truth anchor** — `test_tunnel_corner_cap_is_realistic` confirms cap = 63.19 m/s from A0=3.2 g, A2=0.00032, κ=0.011, ρ=1.18 — independently verified by spot-check computation (63.19 m/s, within [63, 66]). `# TODO(#525)` present at line 470. `G_MS2` imported from `src.physics.braking_fit` at line 82, NOT redefined. PASS.

---

## TOP CHECK — Convention A UNBROKEN

**This is the key result of Option A, and it passes cleanly.**

The rework strategy is entirely different from the first attempt: instead of fixing the SHARED consumer (which broke the convention-A m/s² path that `sim_evaluator`/`fit_batch` use), it converts g-units → m/s² at the `car_prior` boundary ONLY — exactly mirroring the #518 G5 `p_max/MASS_KG` conversion in `_build_longitudinal`. The consumer is untouched.

Consumer files (`physics_data_models.py`, `physics_simulator.py`, `capability_envelope.py`, `lateral_view.py`, `regime_utilization.py`) have ZERO lines changed — confirmed by empty `git diff` output.

Full physics region test run (live, run during this review):
```
py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q
→ 642 passed, 6 skipped in 297.88s
```

**NO test re-baselining required.** Consumer tests (`test_physics_data_models.py` 37 tests, `test_physics_simulator.py` 13 tests, `test_capability_envelope.py` 13 tests, `test_sim_evaluator.py` 9 tests, `test_regime_utilization.py` 22 tests) all pass UNCHANGED — their expected values were not modified because the consumer itself was not touched. The first attempt required 9 re-baselined files; this rework required zero. This is the structural proof that the legacy/`sim_evaluator`/`fit_batch` convention-A m/s² path is intact.

---

## Scope drift
No drift. Exactly two files changed. All specifically excluded consumer, producer, and store-schema files are byte-identical to HEAD.

---

## Evidence verdict
Evidence is present and strongly demonstrates the behavior:

- **TDD red-green:** documented in `g2-implement-result.md` — 2 failed (tunnel cap 17.36 m/s; A0=3.2 raw) → 30 passed (cap 63.19 m/s; A0=31.392). Consistent with the diff (the conversion is the minimal change required).
- **Full region pass:** independently run and confirmed — 642 passed / 6 skipped, zero failures, zero value changes in consumer tests.
- **Simplification limits:** `PASS (2 files checked)`.
- **Independent spot-check:** computation of tunnel cap from A0=3.2 g, κ=0.011, ρ=1.18 confirms ~63.19 m/s.
- **A2 exactness:** independently verified `A2_param * air_density == A2_g * G` to float precision.
- **Covariance Jacobian (diagonal case):** independently verified `(0.15·G)² = 2.165312`, `(3e-5·G/1.18)² = 6.22e-8`, off-diagonal = 0.0.

---

## Code/doc quality
- Module docstring table (lines 41–43) updated to reflect the g→m/s² conversion — accurate.
- `_assemble_lateral` docstring is a full G5-style explanation: store convention, consumer convention, conversion formulas, exactness condition, Jacobian description, default-fallback caveat, and `# TODO(#525)`. Exactly the right level of documentation for a unit-convention boundary.
- Jacobian computed once (`jac` at line 485) and applied once (`jac @ lat_cov @ jac.T` at line 505) — clean structure covering both blob and diagonal paths through the same transform.
- else-branch (defaults) correctly does NOT reference `s0`/`s2` — explicit and readable.
- `G_MS2` imported (not redefined) — consistent with project style (cf. `MASS_KG` import in `_build_longitudinal`).
- Simplification limits: PASS.

---

## Map impact verdict

- **Evidence supports claimed change:** Yes. The produced evidence (63.19 m/s tunnel cap, 642 green, no re-baselining) backs the claimed capability change and the claimed convention-A path preservation.
- **Constraints not violated:** The key invariant — same `air_density` flows from `build_car_ceiling` to `_assemble_lateral` and to the consumer — holds (verified in code: `air_density` computed once in `build_car_ceiling`, passed to `_assemble_lateral`, and passed to `CapabilityEnvelope.from_parameters`). The implementer correctly documents this as the exactness condition to carry forward.
- **Notes match the diff:** Map Impact notes in `g2-implement-result.md` accurately describe the structural anchor, new `air_density` parameter, `G_MS2` import, capability change, and exactness invariant. `as_of_means` reporting converted values is also called out in out-of-scope observations.
- **Decision candidates surfaced:** `decision:ideal_lap_sim_two_sided_evaluator` (G5 p_max boundary-conversion precedent) and `decision:c1_driver_utilization_design` correctly referenced. No new unresolved decisions introduced.
- **Durable context routed:** Triage candidate #525 (repo-wide unit-convention audit) flagged in both the code (`# TODO(#525)`) and the implement result. Mixed-convention defaults smell also called out as a #525 item.

No block on map impact.

---

## Reconciliation check
No architecture divergence requiring Commander reconciliation beyond the already-captured #525 triage candidate. The boundary-conversion pattern mirrors the existing #518 G5 `_build_longitudinal` precedent — an established structural idiom. `as_of_means` now reports converted (m/s²-convention) values; correctly noted as intentional in the result. No consumer of `as_of_means` lateral values found in the touched scope.

---

## Per-check findings

| Check | Result | Note |
|---|---|---|
| r0 context | pass | Handoff, implement-result, diff, engine-config loaded; consumer files confirmed byte-identical. |
| r1 handoff compliance | pass | All four close criteria satisfied (see above). |
| r2 scope drift | pass | Exactly two files changed; all excluded files byte-identical to HEAD. |
| r3 evidence | pass | 642 passed/6 skipped confirmed by live run; no re-baselining; simplification limits PASS. |
| r4 quality | pass | G_MS2 imported not redefined; TODO(#525) present; Jacobian structure correct; fallback branch untouched by conversion; docstring complete. |
| r5 reconciliation | pass | Map-impact notes accurate; #525 triage candidate correctly filed; no Commander reconciliation needed before merge. |
| r6 convention-A unbroken | **pass** | Consumer untouched; full region green with NO re-baselining; `sim_evaluator`/`fit_batch` m/s² path structurally intact. |

---

## Blockers
None.

---

## Out-of-scope observations
- `as_of_means["A0"]/["A2"]` now report converted m/s² values (intentional — matches what the consumer sees). Any future diagnostic expecting raw store g-units from `as_of_means` would need to read the store directly. #525 should audit.
- Mixed-convention defaults (`cfg.default_A0/default_A2` in m/s², store in g-units) are spanned by the same function's two branches. The branch-the-conversion fix is correct and local; #525 should unify conventions so this dual-units hazard cannot recur.
- The `air_density` exactness invariant (same ρ at boundary and consumer) is now a load-bearing assumption. If a future change feeds the consumer a different ρ than `car_prior` computed, A2 exactness degrades to an approximation. #525 should make this invariant explicit in tests or eliminate the dependency.

---

## Workflow Feedback

- **Handoff gaps:** The handoff was thorough and self-consistent. The one gap (also noted by the implementer): the handoff said "build a ceiling from a g-unit store row (A0≈3.2)" for the NEW truth anchor but did not flag that the EXISTING L1 `test_lateral_A0_A2` assertion (`A0==26.0`) would necessarily flip to converted values. The implementer handled it correctly (re-pointing to assert `A0 == 3.2 * G_MS2`), but a one-line "expect to re-point the existing L1 lateral_A0_A2 assertion to converted values" would have removed ambiguity about whether that counted as scope creep. As reviewer, this required a close read of the test diff to confirm it was correctly re-targeted rather than an accidental change.

- **Context rediscovered:** None for this reviewer. The handoff named the conversion, the consumer convention, the exactness condition, and the fallback landmine explicitly enough that the diff could be verified without additional source diving.

- **Instructions improvised around:** The `references/checklist-engine.md` referenced by the skill does not exist at the given path in this installation. Used the engine script directly and drove the survey JSON manually (recording results directly in JSON rather than via CLI). For a survey checklist there are no postconditions to enforce, so the engine verbs are `record`/`flag-candidate`/`consolidate` only — these were applied correctly. The survey JSON is saved at `.agent-work/522-phase-align-utilization/g2-review-survey.json`.

- **What would have made this easier:** One concrete addition to the handoff: a note that the existing L1 `test_lateral_A0_A2` assertion is expected to change (asserting converted values), to avoid reviewer uncertainty about whether the test re-pointing was intentional or scope creep. Everything else was well-specified.

---

## Return status
`complete`

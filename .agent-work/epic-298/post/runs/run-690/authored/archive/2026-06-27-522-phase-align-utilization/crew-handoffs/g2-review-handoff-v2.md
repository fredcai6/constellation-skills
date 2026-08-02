# Reviewer Handoff — G2 Option A rework review (#522)

## Gate
g2-review (REWORK review). The first attempt fixed the shared consumer for g-units and was BLOCKED (it broke the live convention-A `sim_evaluator`/`fit_batch` path). The rework discards that and instead converts the g-unit store → m/s² at the **`car_prior` boundary only**, leaving the shared consumer untouched. This review verifies the rework.

## What Was Implemented (the rework)
- The first-attempt diff was discarded (`git checkout -- src/physics tests/...`); the consumer files are back to their convention-A m/s² baseline.
- In `src/physics/utilization/car_prior.py` `_assemble_lateral`: `build_car_ceiling`'s `air_density` is threaded in, and **store-pooled** g-unit A0/A2 are converted to m/s²: `A0_param = A0_mu·G`, `A2_param = A2_mu·G/air_density`; 2×2 covariance via Jacobian `J = diag(G, G/air_density)`. `G_MS2` imported from `braking_fit.py`. A `# TODO(#525)` marks it the localized Option-A patch.
- The **default-fallback** branch (`cfg.default_A0=30`/`default_A2=0.001`, which are convention-A **m/s²**) passes through **UNCONVERTED** (a Commander-caught fix — uniform ×G would have made the fallback ~30 g).
- Mirrors the existing #518 G5 `_build_longitudinal` `p_max/MASS_KG` boundary conversion.
- Result: `crew-handoffs/g2-implement-result.md`.

## How to Inspect the Diff
Uncommitted on `feat/522-phase-align-utilization` (main checkout): `git --no-pager diff -- src/physics tests`. The diff must be EXACTLY `src/physics/utilization/car_prior.py` + `tests/unit/physics/test_car_prior.py`.

## Close Criteria (each a review check)
1. **Diff scope** is exactly the two files above; `physics_data_models.py`, `physics_simulator.py`, `capability_envelope.py`, `lateral_view.py`, `regime_utilization.py`, the store schema are BYTE-IDENTICAL to baseline (`git diff` shows nothing there).
2. **Conversion math correct & exact:** `A0_param = A0_mu·G`; `A2_param = A2_mu·G/air_density` with the SAME `air_density` that `build_car_ceiling` passes to `from_parameters`/the sim, so `A2_param·air_density == A2_mu·G` (exact). Covariance Jacobian `J·cov·Jᵀ` applied on BOTH the diagonal-σ path and the representative-blob path.
3. **Default fallback physical:** the m/s² `default_A0`/`default_A2` are NOT ×G-converted; a no-lateral-data ceiling yields ~2–6 g (NOT ~30 g). Confirm the new test `test_no_lateral_data_fallback_is_physical` asserts this.
4. **Truth anchor:** the C1-path test builds a ceiling from a g-unit store row and the Monaco-tunnel cap (κ≈0.011, via the real `_compute_speed_caps`) is ~63 m/s (vs VER 63.3) — RED before the conversion, GREEN after.

## TOP CHECK — convention A must be UNBROKEN (the whole point of Option A)
The first attempt's failure was breaking the legacy m/s² path. Independently confirm the rework does NOT:
- The shared consumer (`lateral_capability`/`_compute_speed_caps`/`_gsat_ceiling`/envelope) is untouched, so the `sim_evaluator` (`run_sim_evaluator.py` → `fit_session_full` → m/s² params) and `fit_batch` paths still read m/s² correctly. Verify by inspection (consumer unchanged) AND by running the full physics region with NO test re-baselining required (contrast the first attempt, which needed 9 files re-baselined). If any consumer/known-answer/property test needed a value change, that's a red flag — investigate.
- Run: `py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q` → expect ~642 passed / 6 skipped, no re-baselining.

## Other checks
- Independent spot-check: recompute one corrected cap from a real producer A0 (~3.2 g, κ≈0.011) → ~63 m/s.
- `# TODO(#525)` present; `G_MS2` imported (not redefined).
- `simplification_limits` on `car_prior.py` passes.

## Allowed Scope (of the change under review)
`src/physics/utilization/car_prior.py` + `tests/unit/physics/test_car_prior.py` only.

## Constraints
`py` launcher; physics-model change → truth-anchored evidence; `constraint:physics_region_no_evo_import`; read-only store/cache via absolute paths.

## Map Anchors (inbound)
Inherits g2-implement anchors: `struct:physics.utilization` (`car_prior._assemble_lateral`/`build_car_ceiling`, sibling of `_build_longitudinal` G5), `decision:ideal_lap_sim_two_sided_evaluator` (G5 `p_max` precedent), `decision:c1_driver_utilization_design`.

## Evidence Produced
Truth anchor tunnel cap 17.36→63.19 m/s (RED→GREEN); fallback floor 3.06 g; full physics region 642 passed/6 skipped; diff = 2 files; covariance exactness `A2_param·air_density == A2_g·G` verified.

## Suggested Model Tier
Sonnet — the change is one contained file and the high-risk inverted-convention failure mode is structurally prevented (consumer untouched); the review is verification of a small diff + running the suite + a spot-check.

## Stop Conditions
BLOCK if: the diff touches the consumer/producer/schema; the conversion math is wrong or not exact; the default fallback is non-physical; convention A shows any regression (a consumer/known-answer test needs re-baselining); or the truth anchor doesn't hold.

## Return Format
REVIEW_RESULT to exactly `.agent-work/522-phase-align-utilization/crew-handoffs/g2-review-result.md`: verdict (APPROVE/BLOCK), per-check findings, the convention-A-unbroken evidence, blockers, out-of-scope observations, workflow feedback.

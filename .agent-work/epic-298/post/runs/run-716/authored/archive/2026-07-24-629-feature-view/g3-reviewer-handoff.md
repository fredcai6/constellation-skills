# Reviewer Handoff — G3

## Gate
`g3`

## Survey State Location
`.agent-work/629-feature-view/g3-review/review.json`.

## What Was Implemented
`src/physics/feature_view/build_car_basis.py` — `build_car_basis_posterior_records(store,
year, gp_name, *, model_version)` composes `CarBasisPosteriorRecord` rows from
`EstimateStore` rows, with a `_STATUS_TO_AXES` mapping fanning the 9 status columns out to the
11 physical axes, a nearest-present `prior_session` policy, and a `cross_view_covariance`
passthrough. Plus `tests/unit/physics/feature_view/test_build_car_basis.py` (15 new tests).

## How to Inspect the Diff
Uncommitted working tree, `C:/Programs/f1-629`, branch `feat/629-feature-view`. Read
`src/physics/feature_view/build_car_basis.py` and the new test file directly.

## Task Statement
Full detail: `.agent-work/629-feature-view/g3-implementer-handoff.md`. Full evidence:
`.agent-work/629-feature-view/g3-implementer-result.md`.

## Close Criteria
- **The 9-to-11 axis-status mapping is correct**: verify `_STATUS_TO_AXES` against
  `estimate_store_fields._axis_statuses`'s own construction (source, not memory):
  `cda`->{`drag_area_closed_m2`,`power_drag_area_m2`}, `p_max`->{`max_power_w`},
  `a_b`->{`brake_decel_ms2`}, `b_b`->{`brake_aero_decel_per_m`},
  `a_t`->{`traction_accel_ms2`}, `b_t`->{`traction_aero_accel_per_m`},
  `A0`->{`lateral_mech_grip_g`}, `A2`->{`lateral_aero_grip_g`},
  `theta_R`->{`coast_rolling_decel_ms2`,`coast_drag_area_m2`}. Confirm `normalize_axis_status`
  is applied BEFORE the fan-out (a raw `None` status must normalize to `"unresolved"` before
  being assigned to both governed axes, not after).
- **`cross_view_covariance` is a genuine passthrough**: confirm `fuse_dual_cda` is NOT
  imported/called anywhere in the new file (grep), and confirm by constructing a test case
  yourself where the source `EstimateRecord.cross_view_covariance` has a non-trivial dict
  (e.g. with `fused_cda`/`fused_cda_z` populated) and the produced `CarBasisPosteriorRecord`
  carries the IDENTICAL dict (not a re-derived one with coincidentally-similar values).
- **Reserved fields never fabricated**: confirm no code path in the new file could construct
  a `CarBasisPosteriorRecord` with a non-`None` `process_noise_link`/`parc_ferme_step` — try to
  construct a call that would (should be impossible / caught by G1's `__post_init__` guard).
- **`prior_session`/`chain_position` semantics**: verify the nearest-present policy is what's
  actually implemented and tested (an FP1/FP2/Q chain with FP3 missing gives the Q row
  `prior_session="FP2"`) — try a case the implementer's own tests might not cover (e.g. only
  FP3 and Q present, no FP1/FP2 — does Q's `prior_session` correctly resolve to `"FP3"`?).
- No `src.evo_predictor` import.
- `py -m pytest tests/unit/physics/feature_view -q` green — reproduce count (48 expected: 27+6+15).
- `simplification_limits --paths src/physics/feature_view` clean.

## Allowed Scope
`src/physics/feature_view/build_car_basis.py` (new); `tests/unit/physics/feature_view/
test_build_car_basis.py` (new). Nothing else.

## Specific Exclusions
G1 (`records.py`, `store.py`), G2 (`build_weekend_state.py`) are CLOSED — confirm untouched,
do not flag them as in-scope for this review.

## Constraints the Implementation Must Respect
- `constraint:physics_region_no_evo_import`.
- `cross_view_covariance` is passthrough only — `fuse_dual_cda` never called.
- Reserved fields never fabricated.
- Tests use `tmp_path`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` (read-only), `struct:physics.feature_view`.
- **Capability:** `EstimateStore.load`, the 9-to-11 axis-status mapping.
- **Constraints:** `constraint:physics_region_no_evo_import`.
- **Decision anchors:** decision pressure 2 (reserved slots) — resolved; a float to the
  Admiral on this same decision may still be pending — irrelevant to reviewing THIS gate's
  correctness against the frozen handoff.

## Evidence Produced
See `.agent-work/629-feature-view/g3-implementer-result.md`. Commander independently re-ran
the suite (48 passed) and read `_STATUS_TO_AXES` directly, confirming it matches the mapping.

## Suggested Model Tier
Stronger (Sonnet) — the axis-status fan-out and the missing-session prior_session edge case
are the two genuine correctness risks worth adversarial attention.

## Stop Conditions
Stop and return BLOCK if: the axis-status mapping is wrong for any of the 9 names; a
reserved field can be made non-None; `cross_view_covariance` is re-derived rather than passed
through; evidence is unverifiable.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.

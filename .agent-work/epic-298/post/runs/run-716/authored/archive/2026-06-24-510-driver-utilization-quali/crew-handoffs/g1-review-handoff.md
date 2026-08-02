# Reviewer Handoff

## Gate
g1-review (C1 #510, work-id 510-driver-utilization-quali, branch feat/c1-driver-utilization-510)

## What Was Implemented
A new physics-region package `src/physics/utilization/` with `car_prior.py`: assembles a constructor's **causal
as-of (through-weekend-W)** car-capability ceiling from the cross-session five-view estimate store as a
`PhysicsParameterSet` + propagated covariance wrapped in a `CapabilityEnvelope`. Public API:
`causal_predict(...)` (one-sided GP prediction, no future leakage) and
`build_car_ceiling(*, store_df, year, constructor, target_round, strictly_pre, config) -> CarCeilingResult`.
27 new TDD tests in `tests/unit/physics/test_car_prior.py`. Implementer result:
`.agent-work/510-driver-utilization-quali/crew-handoffs/g1-implement-result.md` (read it in full).

## How to Inspect the Diff
New files only (nothing existing modified): `git status -s` then
`git diff --no-index /dev/null src/physics/utilization/car_prior.py` (or just read the three new files):
- `src/physics/utilization/__init__.py`
- `src/physics/utilization/car_prior.py`
- `tests/unit/physics/test_car_prior.py`
The implementer reports `src/physics/layer2/pooling.py` and all other existing files are UNCHANGED — **verify that
claim** (`git status` should show only the three new files as project changes).

## Task Statement
Build the canonical car-capability ceiling as-of weekend W: causal through-W (and strictly-pre-W) evaluation of the
drift-pooled five-view scalars → `PhysicsParameterSet` + honest covariance → `CapabilityEnvelope`, via the single
canonical sim path, without a second inline scalar sim and without breaking the existing symmetric `DriftFit.predict`.
Full task in `.agent-work/510-driver-utilization-quali/crew-handoffs/g1-implement-handoff.md`.

## Close Criteria (each a review check)
- Causal as-of evaluation **truly excludes future sessions** — a session with clock > W must not change the
  through-W car prior; the strictly-pre-W slice must exclude W's own session. (Confirm the L3 tests actually prove
  this, not just assert it; check the `strictly_pre` clock-shift trick `target_round - 0.5` is sound for integer rounds.)
- The scalar→`PhysicsParameterSet` **bridge is faithful**: `theta_D = cda_closed/(2·MASS_KG)`, `theta_R` from
  coast, power curve from `p_max`, braking `a_b/b_b`, traction `a_t/b_t`, lateral `A0/A2`; sigmas mapped through.
- **Covariance is honest, not nominal**: pooled σ propagates into the sub-parameter covariances.
- The envelope reaches the sim **only** via `CapabilityEnvelope.from_parameters` — **no second inline scalar sim**.
- Inputs validated (field/expectation/actual messages); absent ceiling left `None` (Gsat fallback), not fabricated.
- `constraint:physics_region_no_evo_import` held; `simplification_limits` clean; L1/L3 tests present and green.

## Two specific scrutiny points (the implementer flagged these — judge them)
1. **Clock proxy = `round_idx`, NOT the FIA `upgrade_clock`.** The #492 design uses the FIA cumulative upgrade
   count as the development clock (it de-aliases development from circuit; see `src/physics/layer2/upgrades.py`,
   `pool_driver.py`). The implementer used `round_idx` for test-independence and flagged upgrading later as triage.
   **Judge:** is `round_idx` acceptable for G1's causal as-of ceiling (it is monotone, so causal ordering holds, but
   the drift-rate magnitude / step_var differs from the upgrade-clock design), or is this a BLOCK that must use
   `upgrade_clock`? Recommend treating it as an APPROVE-with-tracked-triage **only if** causal correctness and the
   as-of contract are intact and the divergence is documented; BLOCK if it silently contradicts the dev-clock design
   in a way that corrupts the ceiling. State your reasoning.
2. **Covariance uses the most-recent session's 2×2 blob** (or a diagonal from pooled σ_mu), not a pooled blob. The
   implementer flagged a proper pooled covariance as out-of-scope/deferred. **Judge:** is most-recent-blob honest
   enough for G1 (it is *a* real measured covariance, not nominal), or does it over/under-state uncertainty in a way
   that breaks "honest covariance first-class"?

## Allowed Scope
New: `src/physics/utilization/{__init__.py, car_prior.py}`, `tests/unit/physics/test_car_prior.py`. MAY have added an
additive causal-predict helper (implementer kept it in the new module). Reading-only of layer2/data-models/envelope.

## Specific Exclusions (flag if touched)
No driver utilization (G2); no second inline lap sim; no `scripts/ideal_*` changes; no change to the five-view
estimator or pooling math; no evo-region import.

## Constraints the Implementation Must Respect (each a check)
- `constraint:physics_region_no_evo_import`. Single canonical execution path. Explicit as-of cutoff (no silent
  whole-season/latest fallback). Honest covariance first-class. `py` not `python`. Public input validation.

## Map Anchors (inbound)
- **Structural:** `struct:physics` (new `src/physics/utilization/`); `struct:physics.layer2` (consumed read-only);
  `physics_data_models.py::PhysicsParameterSet`; `capability_envelope.py`.
- **Capability:** new car-prior envelope assembly; consumes `purpose:physics_estimation`, does not change it.
- **Constraints:** physics_region_no_evo_import; as-of contract; single canonical path; honest covariance.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` (Gsat fallback for absent ceiling; canonical
  sim path) — flag any contradiction as a decision candidate.
- **Evidence expectations:** L1 bridge known-answer; L3 causal exclusion; determinism; ceiling fallback.

## Evidence Produced
- `py -m pytest tests/unit/physics/test_car_prior.py -q` → 27 passed.
- `py -m src.utils.simplification_limits --paths ...` → PASS (2 files).
- Implementer reports 460 physics tests pass (no regressions). **Re-run the focused suite to confirm**:
  `py -m pytest tests/unit/physics/test_car_prior.py -q`.

## Suggested Model Tier
Stronger-ish — the causal-correctness and covariance-honesty judgments (scrutiny points) carry the risk.

## Stop Conditions
BLOCK if: the diff cannot be accessed; the causal exclusion is not actually proven; the bridge is unfaithful;
covariance is nominal/fabricated; a second sim path was introduced; an exclusion was touched; or scrutiny point 1/2
reveals a correctness break (not just a tracked simplification).

## Return Format
Return REVIEW_RESULT to `.agent-work/510-driver-utilization-quali/crew-handoffs/g1-review-result.md`: verdict
(APPROVE or BLOCK), per-check findings (incl. an explicit ruling on the two scrutiny points), blockers, out-of-scope
observations, and Workflow Feedback. State the verdict as the literal word APPROVE or BLOCK.

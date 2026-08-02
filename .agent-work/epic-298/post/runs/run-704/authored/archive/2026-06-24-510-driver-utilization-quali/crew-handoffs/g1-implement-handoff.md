# Implementer Handoff

## Gate
g1-implement (C1 #510, work-id 510-driver-utilization-quali, branch feat/c1-driver-utilization-510)

## Task
Build the **canonical car-capability ceiling as-of weekend W** in a NEW physics-region package:
`src/physics/utilization/car_prior.py` (create `src/physics/utilization/__init__.py` too).

Given the cross-session five-view estimate store rows for one `(year, constructor)` and a target round W,
produce the constructor's car capability ceiling as a `PhysicsParameterSet` (+ propagated covariance) wrapped in a
`CapabilityEnvelope`, where the pooled parameters are evaluated **causally** along the development clock:

1. **Causal as-of drift evaluation.** The car prior for W must use sessions **through W** (clock ≤ W's clock) —
   NOT the existing `DriftFit.predict`, which is a *symmetric* kernel smoother (`pooling.py` line ~92: weights by
   `|clock − target|`, so it pulls in sessions *after* W). Add a **causal** predict: a forward random-walk update
   where only sessions at-or-before the target clock contribute, with random-walk variance growing in clock
   distance (reuse the `Var = σ² + step_var·Δclock` shape already in `DriftFit`). Also expose a **strictly-pre-W**
   slice (clock < W) for later predictive use. Put the causal evaluator next to / on top of the existing
   `fit_drift`/`DriftFit` (in `pooling.py` or the new module — your call, but do NOT break the existing symmetric
   `predict`; add, don't repurpose). Per-parameter: predict (μ, σ) as-of the target clock.

2. **Scalar → PhysicsParameterSet bridge (with covariance).** Assemble the as-of pooled scalars into a
   `PhysicsParameterSet` (`src/physics/physics_data_models.py`):
   - `cda_closed` → `LongitudinalParameters.theta_D = cda_closed / (2 * MASS_KG)` (grep for the MASS constant; the
     longitudinal docstring states `theta_D = cda_closed / (2 * MASS_KG)`). Carry `cda_closed_sigma` → `theta_D_std`.
   - `coast_theta_R` → `LongitudinalParameters.theta_R` (rolling). Sigma → `theta_R_std`.
   - `p_max` → a single-point power curve: `theta_P_times=[0.0]`, `theta_P_values=[p_max]` (so `max_power == p_max`).
     Carry `p_max_sigma` into `theta_P_covariance` (1×1).
   - `a_b, b_b` (+ `braking_covariance` blob if present, else build a 2×2 diag from `a_b_sigma, b_b_sigma`) →
     `BrakingParameters(a_b, b_b, covariance)`.
   - `a_t, b_t` (+ `traction_covariance` or 2×2 diag from sigmas) → `TractionParameters(a_t, b_t, covariance)`.
   - `A0, A2` (+ `lateral_covariance` or diag) → `LateralParameters(A0, A2, k_tire=0.0, g_track=1.0, ceiling=...)`.
     (Confirm sensible `k_tire`/`g_track` defaults against how a single-session `LateralParameters` is built
     elsewhere — match existing convention; do not invent.)
   - **Ceiling absent in the store** → leave `LateralParameters.ceiling=None` and rely on the per-car **Gsat
     fallback** path the simulator/`sim_evaluator` already use for missing ceilings (decision
     `ideal_lap_sim_two_sided_evaluator`). Do not fabricate a ceiling.
   - Set `fit_air_density` from the store `rho` (pool/representative value), and the bookkeeping fields
     (`event_id`, `session_type="Q"`, `fit_quality_metrics`) sensibly.

3. **Wrap via the canonical path.** Return / expose the result through
   `CapabilityEnvelope.from_parameters(params, air_density, config)` — the CANONICAL ideal-lap path. **Do NOT add a
   second inline scalar quasi-static sim** (the prototype `scripts/ideal_lap_compare.py` has one; it is being
   retired in G3 — do not copy it).

**Honest covariance:** the pooled per-parameter σ (from the causal as-of evaluation) must flow into the assembled
sub-parameter covariances — not nominal/placeholder values. Where the store carries a covariance blob
(`*_covariance`), prefer it; otherwise build a diagonal from the per-scalar σ. Document the choice.

**Input validation:** validate public inputs (store DataFrame has required columns; constructor present; target
round resolvable to a clock; ≥1 session through-W) with failure messages naming field, expectation, actual value.

## Protected Intent
A trustworthy, leakage-clean **car ceiling** that does not silently include future sessions, exposes honest
uncertainty, and reaches the simulator through ONE canonical path. This is a measurement surface — it must NOT be
wired into evo, and it must NOT over-claim (covariance is first-class).

## Test Mode
TDD required. Physics evidence at the highest applicable L1–L4 level (see CREW_CONTEXT / packets/physics.md
"Truth-Anchored Test Levels"). Tests in `tests/unit/physics/test_car_prior.py`.

## Close Criteria
- `src/physics/utilization/{__init__.py, car_prior.py}` created; a public function/class produces the as-of car
  `PhysicsParameterSet` + covariance and a `CapabilityEnvelope` for a `(store_df, year, constructor, target_round)`.
- Causal as-of evaluator added (through-W *and* strictly-pre-W slices); existing symmetric `DriftFit.predict`
  untouched/unbroken.
- Bridge faithful and covariance propagated from the pooled σ (not nominal).
- `tests/unit/physics/test_car_prior.py` green, covering:
  - **L1 known-answer:** a hand-built store of EstimateRecords → expected `PhysicsParameterSet` channel values
    (theta_D from cda_closed, braking a_b/b_b, traction a_t/b_t, lateral A0/A2, power p_max) and expected as-of μ.
  - **L3 causal exclusion:** adding a session with clock > W does NOT change the through-W car prior for W (the
    leak the symmetric smoother would have). A strictly-pre-W slice excludes W's own session.
  - **determinism** (same inputs → same output) and **missing-channel / absent-ceiling fallback** (ceiling stays
    None; a missing optional channel is handled, not crashed).
- `py -m src.utils.simplification_limits` clean on touched `src/` + `tests/` paths.

## Allowed Scope
- NEW: `src/physics/utilization/__init__.py`, `src/physics/utilization/car_prior.py`,
  `tests/unit/physics/test_car_prior.py`.
- MAY add a causal-predict helper to `src/physics/layer2/pooling.py` (additive — do not change existing behavior),
  or keep it in the new module. Reading: `estimate_store.py`, `pool_driver.py`, `pooling.py`,
  `physics_data_models.py`, `capability_envelope.py`, `physics_config.py`.

## Specific Exclusions
- Do NOT compute driver utilization (that is G2) — stop at the car ceiling envelope.
- Do NOT add a second inline lap sim. Do NOT touch `scripts/ideal_*` (G3).
- Do NOT change the five-view estimator or the pooling math itself (consume as-is; only add the causal as-of read).
- Do NOT import any evo-region package.

## Constraints
- `constraint:physics_region_no_evo_import` — no import of `src.evo_predictor` / `src.latent_power` / `src.compound_prior`.
- Single canonical execution path (consume `CapabilityEnvelope`; no second inline scalar sim).
- As-of contract explicit: the causal cutoff is a named, documented parameter; no silent whole-season/latest fallback.
- Honest covariance first-class (propagate pooled σ; no nominal placeholders).
- Use `py` (not `python`) for all commands. Python 3.14.
- Validate public inputs with field/expectation/actual messages.

## Map Anchors (inbound)
- **Structural:** `struct:physics` (src/physics/, container; new `src/physics/utilization/`); `struct:physics.layer2`
  (`estimate_store.py`, `pool_driver.py`, `pooling.py` — pooled five-view source); `physics_data_models.py::PhysicsParameterSet`
  (bridge target); `capability_envelope.py` (canonical envelope).
- **Capability:** `purpose:physics_estimation` — consumed as the car ceiling, not changed; new car-prior envelope assembly.
- **Constraints:** `constraint:physics_region_no_evo_import`; as-of contract; single canonical execution path.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` — Gsat fallback for absent ceiling; canonical
  sim path. Do not contradict without surfacing a candidate.
- **Evidence expectations:** L1 bridge known-answer; L3 causal exclusion; determinism; ceiling fallback.

## Required Evidence
- `py -m pytest tests/unit/physics/test_car_prior.py -q` output (green).
- `py -m src.utils.simplification_limits <touched paths>` output (clean).
- A short note on the covariance-propagation choice (blob vs diagonal) per channel.

## Verification Commands
```bash
py -m pytest tests/unit/physics/test_car_prior.py -q
py -m src.utils.simplification_limits src/physics/utilization/car_prior.py tests/unit/physics/test_car_prior.py
```
(Data store, if you want a real-data sanity read, is the untracked absolute path
`C:/Programs/f1Brainz/data/physics_estimates.db` — but unit tests must use hand-built in-memory EstimateRecords, NOT
the live DB.)

## Suggested Model Tier
Stronger-ish: the covariance propagation and causal correctness are subtle. Lean on the L1/L3 tests to pin them.

## Authority
Decided (do not relitigate): denominator = cross-session constructor prior (option B); through-W causal posterior is
the characterization cutoff with a pre-W slice derivable; module lives in `src/physics/utilization/`; canonical sim
path = `PhysicsParameterSet → CapabilityEnvelope → PhysicsSimulator`. You may decide: where the causal-predict
helper physically lives (new module vs additive in `pooling.py`); the exact covariance-blob-vs-diagonal rule per
channel (document it); default `k_tire`/`g_track` (match existing convention).

## Stop Conditions
Stop and return if: allowed scope must be exceeded; an exclusion must be touched; the bridge cannot be made faithful
without changing the estimator/pooling math; a decision outside the given authority is needed (e.g. the store lacks
a channel the envelope structurally requires and there is no documented fallback).

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/510-driver-utilization-quali/crew-handoffs/g1-implement-result.md`:
completed slice, files changed, test mode satisfied, evidence produced (paste the pytest + simplification_limits
output), assumptions used, stop conditions hit, out-of-scope observations, and Workflow Feedback (what in this
handoff or the workflow made the work harder than it needed to be).

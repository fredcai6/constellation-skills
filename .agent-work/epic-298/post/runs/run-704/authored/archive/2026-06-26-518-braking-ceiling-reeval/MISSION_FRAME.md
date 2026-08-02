# Mission Frame — #518

## Intent

Make `layer2/decoupled_longitudinal.py` the **canonical longitudinal source** for the
physics capability views (retiring `braking_view.clean_longitudinal_from_raw`, the single
function all three longitudinal views currently call), recalibrate the car-capability
ceiling on the knee-correct braking frontier, and re-run the C1 driver-utilization
characterization to an updated GO/CONTEXTUAL/NO-GO verdict on the braking + fast-corner
regimes — plus characterize and then productize the change across the throttle/coast views.

## Affected Capabilities

- **physics capability-frontier measurement** (`struct:physics.layer2`) — the five-view
  estimator; this run changes the longitudinal input feeding Braking/Traction/PowerDrag/Coast.
- **per-car capability ceiling** (`car_prior.build_car_ceiling` → `CapabilityEnvelope`) —
  recalibrated via the repopulated `EstimateStore` (new a_b/b_b).
- **per-regime driver utilization** (`struct:physics.utilization`) — the C1 re-eval consumer;
  `U_braking`/`U_fast_corner` are expected to fall off the 2.0 clip.

## Examples / Events

- Bahrain heavy-braking: raw ~5.3 g knee the smoother under-read to ~4.0 g; the decoupled
  estimator recovers it (knee −51 vs raw −52). This is the capability the ceiling was missing.
- `EstimateStore` repopulation is the boundary event: new braking (and possibly throttle/coast)
  scalars flow store → `car_prior` → envelope → C1.

## Structural Anchors

- `struct:physics.layer2` — `src/physics/layer2/` (component): `decoupled_longitudinal.py`,
  `braking_view.py` (`clean_longitudinal_from_raw`, `BrakingView`), `session_braking.py`,
  `session_traction.py`, `session_coast.py`, `scoreboard.py` (`CaseInputs`),
  `session_estimator.py`, `estimate_batch.py`, `estimate_store.py`.
- `struct:physics.utilization` — `car_prior.py`, `regime_utilization.py`, `characterize.py`;
  `scripts/driver_utilization_dashboard.py`.
- `struct:physics` — `braking_fit.py`, `capability_envelope.py`, `physics_simulator.py`.

## Governing Constraints / Assumptions

- `constraint:physics_region_no_evo_import` — no evo-region imports anywhere touched.
- `decision:two_cycle_external_anchor_design` (extended to 1-D) — the soft-force anchor is
  the TV-denoised RAW `a_long`, never re-read from a smoothed trajectory.
- One canonical execution path — `clean_longitudinal_from_raw` retired, not left as a dual input.
- Honest covariance first-class — per-sample `sigma_a` propagated into `sigma_kin`.
- Physics model change → highest-applicable L1–L4 truth evidence with units/bounds/invariants.
- `as-of` causal contract in `car_prior` (round_idx ≤ W) is untouched.

## Decision Anchors & Decision Pressure

- `decision:decoupled_1d_longitudinal` — governs the estimator; flips MEASURED→wired at the
  braking-wiring gate; records the HP calibration basis + the retire outcome.
- `decision:smoother_rounds_braking_knee` — the root cause this run cashes in; its retire
  caveat (clean_longitudinal_from_raw) resolves here.
- `decision:c1_driver_utilization_design` — Review Trigger fires (ceiling recalibration changes
  which U values are trustworthy).
- `decision:ideal_lap_sim_two_sided_evaluator` — the ceiling-evaluator contract C1 consumes.
- **Decision pressure (surface to human):** (a) retire/keep `clean_longitudinal_from_raw` —
  ratified by the G2 side-by-side numbers; (b) per-session vs global HPs from G1; (c) any wider
  view that REGRESSES under the decoupled input — fix-or-hold, not blind cut-over.

## Claims / Evidence Surfaces

- Scoreboard acceptance (`scoreboard.py`): braking_knee-vs-raw + non_throttle_ringing — re-confirm
  across the season at G1, and that the wired path preserves it at G3.
- `EstimateStore` repopulation reproducible; C1 dashboard regenerates from the new store.
- BrakingView L1–L4 tests; the `−g·sinθ` de-conflation removal must keep the gravity correction
  exactly once (now inside the estimator via F_vehicle).

## Map Confidence / Staleness / Disputes

- `struct:physics.layer2` + `struct:physics.utilization`: **high confidence**, freshly reconciled
  (#496/#507, #510). Low staleness risk. No scout gate needed.
- The `decoupled_longitudinal` HP defaults are explicitly flagged in the packet Known Limits as
  VER/3-circuit — the G1 calibration directly addresses that flagged limitation.

## Out of Scope

- C2 #511 race-state, C3 #512 regime-vector, C4 #513 FP-session fits (later C children).
- M2/M6 process-model replacement (rejected unless the 1-D filter fails validation).
- Multi-year calibration; only 2023-Q this run.
- Routing physics through the artifact/loaders boundary (separate open question → triage).

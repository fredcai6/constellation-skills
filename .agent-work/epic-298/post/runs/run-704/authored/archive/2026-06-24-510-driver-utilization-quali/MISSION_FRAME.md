# Mission Frame — C1 Driver utilization on quali (#510)

## Intent

Add a physics-region, **measured-not-wired** per-(driver, quali-session) **driver-utilization** capability:
realised lap vs the constructor's cross-session, week-to-week-updated capability **frontier**, decomposed per
regime (slow corner / fast corner / braking / straight) with **honest covariance**, surfaced on a traceable
dashboard and carried to a GO/CONTEXTUAL/NO-GO verdict. Productionizes the existing diagnostic prototypes
(`scripts/ideal_vs_actual.py`, `scripts/ideal_lap_compare.py`) to the spec §4 done-done bar.

## Affected Capabilities

- `purpose:physics_estimation` (Vehicle-dynamics parameter estimation; `struct:physics`) — C1 **consumes** its
  pooled five-view output as the car ceiling; it does not change the estimation itself.
- *ideal-lap simulation* + *two-sided fit evaluation* (capability anchors on
  `decision:ideal_lap_sim_two_sided_evaluator`) — C1 **extends** the two-sided evaluator into the
  driver-utilisation layer the decision named as its Review Trigger: the sim-vs-real gap becomes the per-regime
  driver signal.
- New: *driver utilization measurement* (per-regime extraction of the car frontier) — the capability this run adds.

## Examples / Events

- A driver who matched the car's measured frontier in slow corners but lost time on straights → high slow-corner
  utilization, lower straight utilization; the per-regime split is the readout.
- Both teammates jointly define the constructor frontier through weekend W; each driver's realised lap is scored
  against that shared ceiling (envelope = car, utilization = driver).
- The car-prior envelope for weekend W is the causal through-W posterior along the development clock; a strictly
  pre-W slice is derivable for later Phase-P predictive use.

## Structural Anchors

- `struct:physics` — `src/physics/`, container. Lands the new utilization capability + the canonical car-prior
  envelope assembly.
- `struct:physics.layer2` — `src/physics/layer2/`, component. Source of the pooled five-view estimate
  (`estimate_store.py`, `pool_driver.py`, `pooling.py` drift) the car prior is built from.
- `src/physics/sim_evaluator.py` — the seed; Δv / braking-zone diagnostics promoted into the regime estimator.
- `src/physics/capability_envelope.py` + `physics_simulator.py` — the canonical ideal-lap path the car prior
  feeds (vs the inline scalar quasi-static sim in `ideal_lap_compare.py`).
- `src/physics/physics_data_models.py::PhysicsParameterSet` — bridge target for the pooled scalars.

## Governing Constraints / Assumptions

- `constraint:physics_region_no_evo_import` — **C1 stays a physics-region measurement**; no import of / wiring into
  `evo_predictor` / `latent_power` / `compound_prior`. (Out of scope: any evo feature.)
- DB-only for analysis data (`ORCHESTRATOR_CONTEXT` canonical-data constraint); physics may read the **offline
  FastF1 cache** for raw quali telemetry (existing region posture), not live calls.
- Time-dependent inputs need an explicit **as-of contract** (planning invariant): the car prior for W declares its
  causal cutoff; no silent latest-value/whole-season fallback.
- Single canonical execution path (project doctrine) — see decision pressure below.
- Honest covariance is first-class; the car/driver split is **correlated/impure by construction** (joint
  observation) and the artifact must own that, not engineer it away.
- Physics-model evidence at the highest applicable L1–L4 level.

## Decision Anchors & Decision Pressure

- `decision:ideal_lap_sim_two_sided_evaluator` (current) — the sim is a CEILING evaluator; per-point Δv is the
  primary read; small gap = under-call suspect. **Its Review Trigger fires on this run** ("the driver-utilisation
  layer … consumes the gap as signal") → reconcile/extend at the map step.
- `decision:traction_own_measured_frontier`, `decision:smoother_rounds_braking_knee` — govern the frontier
  semantics the car prior inherits; not changed.
- **Decision pressure (surface to human):**
  1. **Module placement** — new `src/physics/utilization/` package vs adding to `layer2/`. (Durable structure.)
  2. **Canonical ideal-lap sim path** — consolidate the car-prior ideal lap onto
     `PhysicsParameterSet → CapabilityEnvelope → PhysicsSimulator` and supersede the inline scalar quasi-static
     sim in `ideal_lap_compare.py` (single-path doctrine), vs keeping both.
  3. **Causal cutoff** — through-W posterior is the characterization denominator (predictive pre-W slice derivable);
     confirm this is the as-of contract.

## Claims / Evidence Surfaces

- The bridge is faithful: a known `EstimateRecord` maps to the expected `PhysicsParameterSet` channels
  (`cda_closed→theta_D`, `coast_theta_R→theta_R`, `p_max→power`, `a_b/b_b→braking`, `a_t/b_t→traction`,
  `A0/A2→lateral`) — re-confirm with an L1 known-answer test.
- The as-of evaluation is causal: a session after W cannot change the W envelope — re-confirm with an L3
  exclusion test.
- Utilization is well-posed: a synthetic driver riding the frontier scores ≈1 per regime; a uniformly-0.9 driver
  scores ≈0.9; the regime partition tiles the lap — L1/L2 tests.
- Covariance is honest: utilization σ grows with envelope σ and lap-sampling noise; calibration not nominal.

## Map Confidence / Staleness / Disputes

- `struct:physics` / `struct:physics.layer2` — **high confidence, current** (reconciled through #508/#492). No
  scout gate needed.
- Open question in `physics.md`: "trajectory consumption bypasses the artifact boundary" — **orthogonal** to C1
  (already routed to Triage); C1 does not touch the trajectory artifact boundary. Note, do not resolve here.

## Out of Scope

Wiring into evo / any evo feature (Phase P / #450); the predictive pre-W slice *consumption*; race-state
correction (C2 #511); the FP-session enabler (C4 #513); non-quali sessions; changing the five-view estimator or
the pooling math itself (consume as-is); the trajectory artifact-boundary question.

# Reconcile Brief — C1 Driver Utilization on Quali (#510)

For the Cartographer. Fold these landed, reviewed changes into the **current** architecture map
(`docs/architecture/`). Branch `feat/c1-driver-utilization-510`. All three gates APPROVED; reviews are durable at
`.agent-work/510-driver-utilization-quali/crew-handoffs/g{1,2,3}-review-result.md`.

## What landed (current code truth)

A new physics-region package **`src/physics/utilization/`** — a measured-NOT-wired driver-utilization layer:

- **`car_prior.py`** (G1) — `build_car_ceiling(store_df, year, constructor, target_round, strictly_pre, config) ->
  CarCeilingResult(params, envelope, ...)`. Assembles a constructor's **causal as-of (through-weekend-W)**
  car-capability ceiling from the cross-session five-view estimate store (`struct:physics.layer2` `estimate_store`/
  `pooling`), bridging the store scalars → `PhysicsParameterSet` + propagated covariance → `CapabilityEnvelope`. Adds
  a NEW one-sided causal `causal_predict` (the existing symmetric `DriftFit.predict` is untouched). Reads
  `struct:physics.layer2` read-only; reaches the sim only via the canonical `CapabilityEnvelope.from_parameters`.
- **`regime_utilization.py`** (G2) — pure core `regime_utilization(...)` + wrapper `estimate_driver_utilization(...)`.
  Per-(driver, quali) driver utilization vs the G1 ceiling, decomposed into four tiling regimes (braking / slow_corner
  / fast_corner / straight), with honest covariance propagated from the envelope (MC over sampled ceiling params via
  `PhysicsSimulator`). Reuses `sim_evaluator` Δv helpers (no duplicate path). Carries `split_is_impure=True`.
- **`characterize.py`** (G3) — canonical orchestration seam (G1 → realised lap via `session_fit`/`ribbon` → G2),
  returning tidy per-regime `UtilizationRow`s. Consumed by `scripts/driver_utilization_dashboard.py`.

**Single-path canonicalization (user decision enacted):** the inline scalar quasi-static ideal-lap sim (`sim_lap`)
and its `_params` bridge prototype were REMOVED from `scripts/ideal_lap_compare.py`; `scripts/ideal_vs_actual.py`
was retired too. Both are now RuntimeError stubs. The ONE canonical ideal-lap path is now
`EstimateStore → car_prior.build_car_ceiling → CapabilityEnvelope → PhysicsSimulator`. (Triage notes: stub deletion +
`scripts/ver_monza_kde.py` repair are routed to follow-up; not yet done.)

## Map implications to reconcile

1. **New structure:** add `src/physics/utilization/` under `struct:physics` (a new sub-package/component sibling to
   `struct:physics.layer2`) in `packets/physics.md` — three modules above, with the read-only dependency on
   `struct:physics.layer2` (estimate store + pooling), and dependencies on `physics_simulator`/`capability_envelope`/
   `sim_evaluator`/`ribbon`/`session_fit`. It is **prediction-isolated** (no evo import) — same posture as the rest of
   physics; note it is measured-not-wired.
2. **New capability:** a `purpose:physics_utilization` (or similarly named) capability — per-regime driver
   utilization (envelope = car, utilization = driver). Anchor it to `struct:physics` / the new package.
3. **Decision anchor `decision:ideal_lap_sim_two_sided_evaluator` — its Review Trigger FIRED.** That anchor's trigger
   was literally "the driver-utilisation layer (capability-vs-actual decomposition) landing, which consumes the gap as
   signal." It has now landed. Update that anchor (or add a companion decision anchor) to record: the driver-utilisation
   layer exists; the sim-vs-real gap is consumed per-regime; and the **characterization finding** that the current
   car-prior ceiling systematically UNDER-CALLS braking + fast-corner capability (U clips at 2.0 across the 2023-Q
   subset; slow-corner also U>1) — consistent with `decision:smoother_rounds_braking_knee` / the #496 braking-knee
   under-call — so those regimes are NOT yet trustworthy. This is durable "why" worth anchoring.
4. **Consider a new decision anchor** for the C1 design choices that are costly to rediscover: denominator = the
   cross-session, week-to-week-updated (causal through-W) constructor capability prior (NOT season-average, NOT the
   driver's own fit); both teammates incl. the measured driver define the frontier; the car/driver split is
   acknowledged impure (joint observation) and owned by covariance; single canonical ideal-lap path. (Your call
   whether this is one anchor or folded into the updated two-sided-evaluator anchor.)
5. **Scripts:** note `scripts/ideal_lap_compare.py` + `scripts/ideal_vs_actual.py` are retired stubs (the inline sim
   path is gone) if the map references them anywhere.

## Out of scope for reconcile
Do not change code. Do not resolve the open "trajectory artifact-boundary" question (orthogonal). Future work
(the triage candidates tc1–tc10, incl. the #496 ceiling-recalibration reachback) routes to Triage, not the map —
record only current truth.

## Verdict context (for your awareness, not a map edit)
C1 readiness = **CONTEXTUAL** (recommended, awaiting user ratification): straight + slow-corner carry circuit-level
signal; braking + fast-corner NO-GO pending ceiling recalibration. The pipeline is mechanically correct.

# C1 — Driver utilization on quali: resolved understanding (#510)

**Spine:** 510-driver-utilization-quali · **Parent:** #509 · **Spec:** `docs/superpowers/specs/2026-06-24-physics-predictive-pipeline-pathway.md` §7
**Phase C, output 1.** Characterization — **measured, NOT wired** into evo.

## Capability being added (behavior, present tense)

The physics region gains a **per-(driver, quali-session) utilization measurement**: how much of the
constructor's achievable lap the driver extracted, and with what consistency, **decomposed per regime**
(slow corner / fast corner / braking / straight), carrying **honest covariance**.

It is the **driver residual** against a **car capability ceiling** — `envelope = car, utilization = driver` —
built by promoting the existing two-sided ideal-lap diagnostic (`sim_evaluator.py`, decision
`ideal_lap_sim_two_sided_evaluator`) from a *model-under-call* read into a *driver-skill* measurement.

## Resolved design decisions (this interrogation)

1. **Denominator = cross-session constructor capability prior (option B), NOT the driver's own fit and NOT a
   season-average point estimate.** It is a **week-to-week-updated prior**: each session is a new observation
   that updates a state-space/drift posterior over the car's capability along the development clock
   (`pooling.fit_drift` random-walk-along-upgrades is the substrate).

2. **The prior is updated *through* weekend W using W's own sessions (contemporaneous), and the measured
   driver is NOT left out.** Rationale (user): the team's drivers *together* define the car's maximum possible
   capability frontier; dropping the lead driver yields a degenerate envelope. The "driver bit" is how much /
   how consistently the driver extracts that frontier. Driver and car are only ever observed jointly, so the
   split is **correlated and impure by construction** — the covariance and the readout interpretation must own
   that caveat; it is NOT engineered away.

3. **Causality gap surfaced:** `DriftFit.predict(clock_target)` is today a **symmetric kernel smoother** (weights
   sessions by `|clock − target|`, pulling in *future* sessions down-weighted), not the causal week-to-week
   filter the model describes. C1 makes the as-of evaluation causal so the prior carried into W uses past
   sessions and W updates it — and so a strictly-predictive slice (sessions < W, for Phase P) is also derivable.
   The characterization itself is measured on the **through-W** posterior.

4. **The envelope is the maximum-capability *frontier*** (upper bound), consistent with layer2
   `kernel_upper_ridge` being "capability, not utilisation" — so including the driver's own laps does not
   collapse the gap to zero.

## What this pulls into scope

- A **scalar → `PhysicsParameterSet` bridge** (with covariance): the #492 five-view pooled estimate emits
  five-view scalar parameters + σ, but the simulator/`CapabilityEnvelope` consumes a `PhysicsParameterSet`.
  The car-prior ceiling must reach the simulator as a parameter set (or an equivalent frontier-based envelope),
  with the pooled σ propagated into the envelope and on into the utilization covariance.
- A **causal as-of evaluation** of the drift prior (through-W posterior; predictive slice derivable).
- **Per-regime decomposition** of realised-vs-ceiling Δv into slow corner / fast corner / braking / straight
  (the seed only restricts to braking today). Regime boundaries (e.g. slow/fast corner by the downforce-loading
  v²κ threshold) are a method detail to settle at plan time.
- **Honest covariance** propagation: envelope covariance + lap-sampling → utilization σ, calibrated, owning the
  car/driver correlation caveat.
- A **traceable utilization dashboard** (raw → plotted readout, reproducible) and a recorded **readiness verdict**
  (GO / CONTEXTUAL / NO-GO).

## Protected intent (must not break)

- **No evo wiring** — `constraint:physics_region_no_evo_import`. C1 is a physics-region measurement surface only.
- **Honest covariance is first-class**; do not over-claim a clean car/driver separation the observations cannot
  support.
- **Single canonical execution path** — no shims/dual formats/fallback branches (project doctrine).
- **DB-only for analysis data**; physics may use the offline FastF1 cache for raw quali telemetry (existing
  region posture), not live calls.
- Decision anchor `decision:ideal_lap_sim_two_sided_evaluator` carries a **Review Trigger** that *this work*
  fires ("the driver-utilisation layer … consumes the gap as signal") → reconcile at the map step.

## Reachback flagged (per spec)

Race utilization is confounded by tyre-deg/fuel; this quali version is the **clean anchor**, to be revisited
once the race-state output (C2 #511) lands. If set aside before done-done, leave a pick-up note on #510.

## Out of scope for C1

Wiring into evo; the predictive-prior (sessions<W) *consumption* (Phase P / #450); race-state correction (C2);
the FP-session enabler (C4 #513); any non-quali session.

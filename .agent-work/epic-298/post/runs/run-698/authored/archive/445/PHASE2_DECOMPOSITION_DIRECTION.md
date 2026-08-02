# Phase 2 (#449) Direction — capability decomposition (user, 2026-06-13)

Frame #449 by OUTCOMES, not module surgery. Goal: decompose lap performance into car-capability
components vs driver skill. Everything the estimator yields is force/mass with honest covariance;
Phase 2 attributes it to physical sources (car/conditions), and the unexplained car-independent
remainder is the driver. Each axis is an identifiability problem with a confound and a lever:

## a) Aero — Cd (drag) + Cl (downforce)
- Static across a session → pool the whole session, fixed-parameter fit, covariance shrinks.
- Confound 1: drag is vs AIR speed not ground speed → compensate wind/crosswind using trajectory
  heading + session weather (wind speed/dir); else tailwind reads as low drag. Crosswind = side force.
- Confound 2: Cd & Cl both ∝ ½ρv² → separable only by CHANNEL: drag in longitudinal coast-down,
  downforce in how lateral grip + braking grow with v². Need both channels.
- DRS = discrete Cd state to condition on (in telemetry), not noise.

## b) Engine power — confounded by mode, lever = RPM & gear
- Capability = torque-curve SHAPE; mode = LEVEL the map sits at. RPM+gear locate the operating
  point → fitting power vs RPM separates shape (car) from level (mode).
- Identify at full-throttle high-gear straights (power-limited regime, drive=P/mv reveals P).
- Honest output likely: power ENVELOPE + a mode-usage signal as separate features (full mode
  de-confounding from few laps is probably beyond the data).

## c) Vehicle mass — degenerate nuisance state, anchored by rules
- Accelerations only reveal force/mass → mass degenerate with every force magnitude.
- Anchors: regulation minimum mass (hard lower bound) + fuel burn (~linear mass decrement per lap,
  near-known rate). Stint-evolution of performance is the observable that pins the fuel-mass slope.
- OD form: m(lap) = m_car + m_fuel0 − burn·lap, priors from the rulebook, slope from how the car
  quickens as it lightens.

## d) Grip — hardest; car-vs-driver split lives here
- Friction-ellipse size; most time-varying (degradation), most coupled (load/downforce-dependent,
  temperature), most driver-contaminated.
- **Compound clarification (user 2026-06-13): borrow the THINKING/solution-shape from the compound
  regularizer work — but PHYSICS-based, not time/lap-time-based. Do NOT wire the evo
  `src/compound_prior/` connection yet.** I.e., a regularizer over compounds grounded in physical
  grip (force the tire transmits) rather than in lap-time deltas; the evo bridge stays for Phase 3.
- THE split: available grip (car × compound × conditions × tire state) = capability; utilization
  (how close to the ellipse, how consistently) = driver skill. Reuse friction_coupling utilization,
  fed honest accelerations.

## Process (user 2026-06-13): EXPLORE before implementing
Do NOT tear into the Phase-2 module. Once #448 lands AND is behaving, run an exploratory LADDER
(same E1-E12 lab style) to derive forces — characterize what the honest acceleration data supports,
test each identifiability axis, THEN design the module against evidence. F-series ladder sketch:
F1 characterize the acceleration/force signal by regime (coast/throttle/corner/brake) + covariance;
F2 drag/aero (wind-compensated, Cd/Cl channel separation, honest covariance); F3 power vs RPM/gear
(shape vs mode); F4 mass/fuel nuisance-state via stint evolution; F5 grip envelope + utilization +
physics-compound regularizer. Branch per results, honest-null welcome. Build #449 only after the
ladder says which decompositions the data actually supports.

## Organizing deliverable
Per (car, session, conditions): identified capability envelopes (aero Cd/Cl, power curve, mass
context, grip envelope) WITH covariance + a driver-attributable residual (utilization, consistency).
Phase 3 turns these into features.

## Two open decisions (for when #449 is written)
1. Compound bridge: grip ↔ src/compound_prior is a physics↔evo coupling; map keeps them decoupled
   until Phase 3. Admiral lean: keep Phase 2 grip physics-pure (car/compound/conditions property),
   connect the compound PRIOR at Phase 3. User to confirm when we write #449.
2. Grip-envelope-as-feature: inside #449 or split to #450 (deferred — decide against real Phase-2
   outputs).

## Discipline (carries from the lab)
Honest-null built in: mass, power-mode, Cd/Cl separation have real identifiability limits in a few
laps. Covariance is the referee — a fit that can't separate drag from downforce returns a fat
covariance and SAYS SO. Everything propagates uncertainty; these are weak confounded identifications
by nature. Front-end note: delete control_alignment + the old kinematic derivation (the estimator's
acceleration state with covariance replaces them); keep/RE-TEST the lumped force forms
(drag/rolling/power, lateral envelope, friction ellipse) against clean inputs, grade by residual
honesty. Write #449 against the concrete acceleration API once #448 lands.

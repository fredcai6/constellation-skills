# Power / longitudinal powertrain — energy-flow model (epic #445 Phase-2)

Power is a managed energy budget, not a coefficient. Longitudinal axis = everything couples (only a_long
observed = sum of drive − drag − roll − engbrake + harvest). Model: ICE capability P_ICE(rpm) + tactical
ERS deploy/harvest, tied by a hidden battery SOC + energy conservation. USER RESERVATION (2026-06-13): SOC
nuisance-state accumulates integrator error + creates cross-segment dependencies — so DON'T fit SOC first;
measure pieces DECOUPLED (lower-envelope), then TEST energy balance as a diagnostic before committing to a
coupled state.

ANTI-THRASH (hard lesson): all power experiments are LIGHT — clean SPEED channel (v, a_long=dv/dt) + rpm/
gear + DRAG-1 drag (CdA~1.0); NO per-lap trajectory-smoother fits. SINGLE bounded foreground run. EVID =
ABSOLUTE path under THIS worktree's .agent-work (don't hardcode a foreign repo path). Never background-and-
end-turn.

## POWER-1 — ICE capability curve from the on-throttle power FLOOR (decoupled, no SOC) [expt-power1]
Question: extract a clean ICE power-vs-RPM curve as the LOWER ENVELOPE of deployed wheel power on
full-throttle segments — ICE = floor (deploy off), ERS deploy = excess above — consistent across drivers
sharing a power unit?
Method: full-throttle segments (Throttle>95%, straight, high gear, low curvature). Wheel power
P_wheel = m·v·(a_long + a_drag + a_roll + g·sinθ); v from clean speed channel, a_long=dv/dt, subtract drag
(DRAG-1 CdA~1.0) + rolling + grade (from raw Z/position; note if flat). LOWER ENVELOPE of P_wheel vs RPM
(per gear) = ICE-only (when deploy≈0, battery saving/empty); excess above = ERS deploy. POOL drivers sharing
a manufacturer power unit (ICE curve shared — like the grip car-envelope). Honest covariance + propagate
drag uncertainty. Output: P_ICE(rpm) floor per power-unit; deploy-excess distribution. Honest-null if the
floor is too contaminated/sparse. Sessions: 2022 Spain R + Austria R (≥2 manufacturers w/ 2 cars each).

## POWER-2 — ERS HARVEST from off-throttle excess (decoupled, no SOC) [expt-power2]
Question: quantify the ERS harvest energy flow from the off-throttle EXCESS deceleration above the aero
floor (DRAG-1's "contamination" IS harvest) — clean/measurable, and what profile?
Method: off-throttle coast + braking segments. Excess decel above the aero+rolling floor (reuse DRAG-1's
lower-envelope CdA~1.0) = harvest+engbrake force; P_harvest ≈ excess_force·v (separate engine-braking — a
~constant overrun torque, rpm-dependent — from ERS harvest — energy-budget-limited — if possible; note the
confound). Braking regen (blended w/ friction brakes) harder — note. Measure harvest profile: magnitude,
where on track, per-lap ∫P_harvest. Honest covariance. Output: P_harvest profile + per-lap harvest energy.
Honest-null if harvest not separable from engine-braking. Sessions: 2022 Spain R + Austria R.

## POWER-3 — Energy-balance DIAGNOSTIC (tests the bootstrap WITHOUT fitting SOC) [staged after 1+2]
Question: does ∫P_deploy (POWER-1 excess) ≈ ∫P_harvest (POWER-2) + regulated per-lap allocation, per lap?
This TESTS the user's concern directly: if deploy and harvest balance cleanly per-lap, the energy-
conservation bootstrap is real and the SOC coupling is usable; if they don't balance (or only balance with
large unexplained residual), the cross-segment coupling accumulates error as feared → SOC-as-state is a
bad idea and we keep the pieces decoupled. Diagnostic only — no SOC state fitted. Staged after POWER-1/2.

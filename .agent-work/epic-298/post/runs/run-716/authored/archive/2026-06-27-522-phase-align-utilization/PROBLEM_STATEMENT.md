# #522 — Phase-align (or per-regime-frontier) the ideal-vs-real utilization comparison

**Resolved problem statement (understand step, cmdr-522).** Parent: #509 C-phase. Supersedes the open braking/fast-corner question from #510 and the #518 NO-GO.

## Capability being changed

The C1 **per-regime driver-utilization** measure (`U_r`, the realised-vs-capability ratio per regime: braking / slow_corner / fast_corner / straight). Today it is **not trustworthy** for braking and fast-corner — both clip at `U_CLIP_MAX=2.0`. This issue makes `U_r` a physically bounded, honest measure (`U≈1` when the driver is at the car's capability, not 2–4×).

## Root cause — verified from code, not the #518 narrative

The ideal lap (`PhysicsSimulator.simulate_lap`) is a correct quasi-static capability ceiling: grip-limited corner-speed caps (`v_corner = sqrt(grip/κ)`), a backward braking pass (brake as late as `braking_grip_limit` allows), a forward traction/power pass, then `min(forward, backward, caps)`. Because it is a true ceiling **on the ribbon geometry**, `v_real ≤ v_ideal` must hold at any shared track point — so the `U`-ratio is bounded by ~1 by construction.

The #518-measured ratios of 3.3–3.8× are therefore **impossible for a correctly-aligned ceiling** → they are a **comparison artifact**, not the real lap beating the car. The current comparison lays the real lap onto the ribbon by *normalized progress* (`resample_by_progress`, `u = s/s_total`); corners do not sit at the same fractional progress in the real lap vs the ribbon, so near a braking knee (200 km/h over a few car-lengths) a small index drift divides a fast-corner real speed by a tight-corner ideal speed.

## Two candidate root causes — gate 1 discriminates them (DO NOT ASSUME)

- **(a) pure misregistration** — ideal corner caps are physical; progress-alignment parks real corners against the wrong ribbon points. → fix = compare on **true track distance / corner landmarks** (the ideal-lap concept survives; we just compare it correctly).
- **(b) under-called corner caps** — the lateral frontier / Gsat fallback under-calls cornering grip, so even a perfectly aligned comparison shows real > ideal. → fix = **per-regime measured-frontier comparison** (drop the ideal-lap denominator; compare realised regime forces to the five measured per-view frontiers — braking A+Bv², lateral grip envelope, power-drag).

Evidence leans hard toward (a) (the ideal lap's top speed and lap time are physical post-#518-G5, so it is not uniformly slow), **but this run verifies it on concrete traces before choosing the fix.** User mandate: "diagnose instead of assume."

## Scope (confirmed with user)

- **Re-run surface:** RBR 2023-Q subset — Monaco / Italy / Great Britain / Singapore, VER (the #518 cases). Wiring the other 4 C1 constructors is OUT (per the issue).
- **Straight under-call (MED secondary):** fold in only if the chosen fix touches the same comparison surface; otherwise note / route to triage. Does not gate the issue or expand scope on its own.
- **Closeout:** verdict-producing — re-assess the per-regime GO/CONTEXTUAL/NO-GO. Honest covariance (envelope σ + lap-sampling σ from #518 G4) preserved.

## Out of scope

The braking estimator / ceiling (done, #518). The sim top-speed units fix (done, #518 G5). Wiring the other C1 constructors. Composing C-outputs into prediction (later #509 P-phase).

## Governing constraints / decisions

- `decision:c1_driver_utilization_design` — denominator = causal through-W constructor prior; both teammates define the frontier; `split_is_impure=True` always; single canonical ideal-lap path. **Review trigger active** (this is the ceiling/comparison recalibration it names).
- `decision:ideal_lap_sim_two_sided_evaluator` — the ideal lap is a two-sided capability evaluator, not a predictor; small gap = suspect (under-call). **Review trigger explicitly names the phase-alignment fix landing.**
- `constraint:physics_region_no_evo_import` — utilization stays measurement-only; no evo import.
- Physics rigor: truth-anchored evidence, units/bounds/invariants explicit; `py` launcher; DB-only.

## Shape of the plan (3 gates)

1. **Diagnose** — concrete traces (ideal-v, real-v, curvature vs true distance) on 1–2 RBR corners → name (a) or (b) with evidence + recommend the comparison method. Evidence-only, no prod change. **Decision checkpoint to user after.**
2. **Implement** the chosen comparison fix (method confirmed at the post-gate-1 checkpoint).
3. **Re-run + verdict** — C1 dashboard on the RBR subset → re-assessed per-regime verdict; honest covariance preserved.

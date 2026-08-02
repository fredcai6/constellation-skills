# Phase-2 Force Ladder — Synthesis & #449 Recommendation (overnight 2026-06-13)

Experiment ladder F1–F6 (lab branches `expt/448-f1..f6`, all pushed; lab mode, no production
changes). Question: which car-capability decompositions does the honest acceleration data support,
separating car from driver? Answer below. F5 (grip detail) harvest pending; headline from F1.

## The one finding that governs everything (F1 → F3/F4 → F6)
Acceleration is a LATENT we infer, never measured. Position is dense, so position+speed χ²≈1 for
both short and long smoother length-scale `ell` — the data barely constrains `ell`, yet `ell` almost
entirely SETS the acceleration covariance (posterior accel sd ∝ 5·sf/ell²; ranged 2.8→401 m/s² at
flat χ²). So acceleration honesty is PRIOR-dominated, and the production `fit_stint_hp` (which
optimizes pos/speed) left `ell` to a per-driver lottery → only ~1 driver/session resolved acceleration.

**F6 resolution:** the data genuinely cannot pin `ell` (honest-null on data-driven jerk-bandwidth ID;
measured brake rise ~0.40s but no single ell fits race+quali). So `ell` must be an ASSUMED physical
constant. **Pin `ell = 4.5 s`** → resolved-driver 4/10→9/10, per-driver accel-sd spread 138×→1.8×
(uniform ~9 m/s² floor). Consistency is the unlock: it makes cross-driver/lap POOLING valid (1/√N),
which is how the small forces get resolved despite being per-sample sub-floor.

## Per-capability verdict (the decomposition)

| Capability | Resolved? | How | For #449 |
|---|---|---|---|
| **Grip** (friction ellipse) | **YES, strong** | edge S/C 8-15 (F5); lateral peak Belgium 3.51g / Britain 4.54g / Spain R 3.33g, physically credible | **The flagship.** Envelope is a SHARED car property (cv across drivers 1.4-1.9%, within bootstrap noise in quali = one envelope = the car); utilization = driver skill, emerges in the RACE (cv 2.7% vs grip 1.4%). → take ENVELOPE from quali (cleanest), UTILIZATION from race. |
| **Drag (Cd)** | **YES, pooled** | coast WLS `−a_long=θ_R+θ_D·ρ·v²`; θ_D≈1.05e-3, CdA≈0.94 m² (F2) | Usable feature, but report the DRIFT-inflated covariance (per-lap scatter 4-5× formal SE), not the naive one. Wind comp ~3% (low-leverage, phase-uncalibrated). |
| **Downforce (Cl)** | **PARTIAL** — via grip, not drag | NOT separable in the drag channel (F2, geometry-confounded); BUT the v² downforce signature IS present in the grip envelope (F5 e2>0 everywhere, strongest in the race) | Recover downforce as the speed-dependence of the GRIP envelope, not from coast drag. A weak-but-real feature; richer probe (track-curvature-normalized) would sharpen it. |
| **Engine power** | **WEAK / relative** | full-throttle drive accel; mode NOT de-confoundable; absolute inflated; only relative index (F3) | Power-envelope as a RELATIVE per-car index; mode-usage must come from a direct telemetry channel (RPM/deploy), not force decomposition. Needs ell=4.5 fix to resolve >1 driver. |
| **Mass / fuel** | **NO** (degenerate) | fuel-burn slope ~400× below the accel floor; trend flips sign with ell (F4) | Keep as an ANCHORED NUISANCE STATE (reg min ~798 kg + assumed burn ~1.75 kg/lap), never fitted. |

## Car vs driver
Grip is where the separation lives and works: available-grip envelope = car×compound×conditions;
utilization (distance to the ellipse boundary) = driver skill. The other channels are car-capability
only (driver doesn't move drag/power-capability). So the realistic Phase-2 car-vs-driver product is:
**grip envelope + utilization**, with aero/power as car-capability indices and mass anchored.

## Recommended #449 shape (outcomes, not module surgery — to be written against the real API)
1. **Estimator config — `ell` must be pinned physically, and it's REGIME-DEPENDENT.** F6 (general
   small-force) recommends ell≈4.5s; F5 (grip on high-curvature flying laps) needs ell≈8-20 (short ell
   interpolates GPS jitter into absurd 100-2000 m/s² corner accel). Same root cause (χ² blind to accel
   variance), different optimum per regime/force magnitude. → A single fixed ell is a COMPROMISE; the
   real answer is **state-dependent roughness** (`NSStintSmoother` + `build_roughness`), already plumbed
   in production — longer effective ell where the path is smooth, shorter where dynamics are genuinely
   fast, set by a physical jerk prior, NOT per-driver fit. Interim: use a fixed physical ell per
   deliverable (grip from a long-ell fit ~10; drag/power from ~4.5) and ALWAYS report ell + posterior
   accel sd with every force; flag |a|<2·sd as covariance-limited. This `ell` choice is the central
   Phase-2 modeling decision (see open decisions).
2. **Front-end:** delete `control_alignment` + the old kinematic derivation (estimator's accel state
   replaces them). Consume a_long/a_lat + covariance from the trajectory artifact.
3. **Deliverables, graded by what's identifiable:** grip envelope + utilization (primary); pooled Cd
   with honest covariance; relative power index; mass anchored. Everything carries covariance; weak
   channels report fat covariance and say so (honest-null is first-class).
4. **Compound:** borrow the regularizer THINKING, physics-based (grip = force transmitted), NOT
   lap-time-based; do NOT wire `src/compound_prior/` (Phase 3).
5. **Re-test, don't assume, the lumped forms** (drag/power/lateral-envelope/friction-ellipse) against
   clean inputs; keep what fits with honest residuals, flag what doesn't.
6. Fold TR-3 (reconcile `measurement_model.md` §9-11 to the trust profile) into this work.

## Decisions
- **The `ell` strategy — DECIDED 2026-06-13 (user): STATE-DEPENDENT.** Let ell vary with the car's
  state via `NSStintSmoother` + a physical jerk prior (shorter where maneuvering hard, longer where
  smooth). "More work is fine, this is a learn-by-messing-around project." This is the principled answer
  F5+F6 pointed at; #449 builds it, not a fixed-ell compromise.

## Bootstrap (G1, 2026-06-13) — mechanism validated, with limits + a new requirement
- The layer-2 information filter WORKS: posterior tightens lap-by-lap; cross-regime information transfer
  (grip→shared downforce→drag) is real and large (corner data pins C_df 34×, buys back +92.6% of sharing
  inflation). The bootstrap architecture is sound → Phase-2 spine = this filter, not independent batch fits.
- LIMIT: it does NOT net-tighten Cd, because coast-drag and downforce-drag are collinear (both ∝v²). →
  source downforce from the GRIP channel; don't try to sharpen coast drag with it.
- TEAMMATE POOLING tightens (1.3-1.6×), more when the teammate samples complementary regimes (Ferrari
  >√2). BUT must be falsification-gated per pair: G1 found Red Bull = same car (pool OK), Mercedes+Ferrari
  = candidate rare exceptions (don't silently pool).
- NEW #449 REQUIREMENT: any per-lap-accumulating filter is overconfident ~×2.6 unless the measurement
  noise R carries the between-lap drift. AND that drift is likely a REAL slowly-varying signal
  (tyre/track/fuel/conditions) — model it as a state, not just inflate it away (ties to grip-degradation).

## Open decisions for the user
- Compound bridge timing (Phase 2 physics-pure vs earlier) — admiral lean: physics-pure now.
- Grip-envelope-as-feature inside #449 vs split to #450.
- Whether the downforce + power channels are worth richer probes in #449 or deferred (they're weak).

## Process note (own it)
F6 and F5 (and E12 earlier) repeatedly turn-ended while backgrounding long compute — the documented
failure mode. F6 self-harvested on resurrection; F5 stalled with scripts committed but no evidence
(recovery in progress). Strong lesson candidate: experiment agents must foreground long compute or
checkpoint per-phase; the launch-order rule needs a structural guard.

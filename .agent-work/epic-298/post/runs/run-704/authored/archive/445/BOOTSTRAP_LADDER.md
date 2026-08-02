# Phase-2 Bootstrap Ladder (G-series) — recursive parameter filter

The shift from batch F-experiments to a LAYER-2 parameter filter: a joint posterior over car (+driver)
parameters, updated lap-by-lap, where physical COUPLING makes resolving one parameter tighten its
correlated neighbors (the bootstrap). Layer-1 = the production trajectory smoother (per-lap forces +
honest covariance). Guardrail ethos (user): constantly try to prove ourselves wrong — held-out scoring,
consistency checks, honest-null if the bootstrap doesn't tighten. State-dependent ell is the DECIDED
direction; G1 uses honest per-regime fixed ell (grip~10, coast/drag~4.5 per F5/F6) as the interim, reports
ell, and notes production will use NSStintSmoother state-dependent ell.

## G1 — Cheapest bootstrap sub-graph: mass + aero + grip, + teammate pooling (worktree expt-g1, branch expt/448-g1)

Question: (1) Does a joint information filter over {mass/fuel, aero Cd+downforce, grip envelope}, fed a
race session lap-by-lap, visibly TIGHTEN — posterior covariance shrinking and the grip→downforce→Cd
coupling tightening the drag estimate as a side effect of resolving grip? (2) Does pooling BOTH
constructor-teammate cars (shared car-state) tighten the shared posterior MORE than one car — and are the
teammates statistically the same car (falsification test)?

### State vector (small, the cheapest coupled sub-graph)
- **mass/fuel:** m_car (prior ~798 kg 2022 reg min, tight-ish), fuel burn rate (prior ~1.75 kg/lap),
  → m(lap)=m_car+m_fuel0−burn·lap. Mass is the master key: it scales every force (accel=F/m).
- **aero:** θ_D (drag, ∝ Cd·A) and a downforce coefficient C_df that enters BOTH the drag q-term AND the
  grip envelope's v²-growth — this shared appearance is the coupling to exploit.
- **grip:** friction-ellipse extents — lateral a_lat0, braking, traction — with speed/downforce
  dependence (envelope grows with C_df·v²). Friction ellipse couples lat↔long.

### Measurement model = the coupling (per-regime, honest covariance from layer-1)
- coast samples: −a_long = θ_R + θ_D·ρ·v²  (drag; a_long=F/m couples mass)
- corner samples: |a_lat| bounded by a_lat_max(v) = (a_lat0 + k·C_df·v²)  (grip + downforce, /m)
- braking/traction: longitudinal grip extents; friction-ellipse shape ties them to lateral
- fuel-burn: anchors the mass evolution across laps
Each lap contributes regime measurements (force ± honest covariance from the smoother). Build the joint
posterior in INFORMATION FORM (accumulate inverse-covariance additively per lap) so degeneracies show as
low-information directions until an anchor/regime fills them.

### What to run & show
1. **Sequential tightening:** initialize broad priors; feed laps 1..N; record the full posterior
   covariance (and the parameter CORRELATION matrix) after each lap. Plot each parameter's sd vs lap, and
   the off-diagonal correlations. Expect 1/√N on well-observed params + cliffs when a degeneracy breaks.
2. **The bootstrap demonstration (headline):** run WITH vs WITHOUT the grip↔downforce↔drag coupling
   active. Show that resolving grip's downforce term tightens the drag Cd covariance via the shared C_df —
   i.e., a measurement in the corner regime sharpens an aero parameter that lives in the coast regime.
   Quantify the Cd-variance reduction attributable to coupling (vs just more data).
3. **Teammate pooling test:** pick ≥1 constructor pair from 2022 Spain R (e.g. Mercedes RUS+HAM, Ferrari
   LEC+SAI, Red Bull VER+PER — choose pairs with full clean stints). Run (a) one car alone vs (b) both
   teammates sharing the CAR state (m_car, aero, grip shared; fuel/lap-phase per-car). Quantify how much
   the shared posterior tightens with two cars (≈√2 if independent; MORE if the teammate samples
   complementary regimes/speeds). Try a second pair if cheap.
4. **FALSIFICATION (guardrail — the user's "prove ourselves wrong"):** before pooling, fit each teammate's
   car-state SEPARATELY and test whether their posteriors overlap within covariance (are they the same
   car within noise, as assumed?). If a teammate is inconsistent beyond noise, report it as a candidate
   "rare exception" (damage/setup/upgrade) OR a sign the coupling model is wrong — do NOT silently pool.
   Also: held-out a lap, predict its forces from the filter, score; posterior-predictive chi² on the
   accumulated parameters (do they reproduce observed accelerations within covariance?).

### Honest-null clauses
- If the bootstrap does NOT tighten (coupling too weak, or covariances inflate when channels are joined),
  that is a complete, important result — report it and diagnose why.
- If teammates are NOT statistically the same car, that falsifies the pooling assumption for that pair —
  report honestly; it's a finding, not a failure.

### Rules
Dogfood the production estimator (`from src.preprocessing.trajectory import ...`); honest per-regime ell
(report it); offline cache `C:/Programs/f1Brainz/outputs/cache` (raw streams, never get_telemetry; pos
decimetres, speed km/h); DB truth `data/f1_data_2022.db`; session 2022 Spain R (clean race, fuel evolution,
multiple constructor pairs); `py` never `python`; numpy/scipy only; evidence JSON+PNG under
`.agent-work/expt-g1/evidence/`; commit+push as you go; checkpoint per-driver smoother fits (they're the
expensive part) so a continuation can resume; FOREGROUND long compute, NEVER background-and-end-turn (this
failure mode hit E12/F5/F6 — poll in foreground ≤10 min). Covariance is the referee.

Return: the per-lap tightening curves + correlation evolution; the with/without-coupling Cd-variance
reduction (the bootstrap headline); the one-car-vs-two-car shared-posterior tightening; the
teammate-same-car falsification verdict; held-out + posterior-predictive checks; ell reported; evidence paths.

## G2 — Segment-integral (weak-form) force estimation vs pointwise (worktree expt-g2, branch expt/448-g2)

User insight (2026-06-13): stop solving for instantaneous acceleration (noisy 2nd derivative, ell-dominated
per F6); solve over REGIME SEGMENTS using INTEGRAL constraints on velocity (clean, ~0.49 m/s per E3).
"v has significantly less uncertainty than a, so our boundary conditions tell us more than we're picking up."
This is the weak/integral (OD batch / multiple-shooting) form vs the strong/pointwise form G1 used.

Question: does the segment-integral formulation dramatically tighten the force parameters — and crucially,
does it RESOLVE POWER (which F3 declared null pointwise) by using throttle-segment ΔV instead of pointwise
a_long? Quantify the tightening vs G1 on the same session/params.

### Formulation
Use the production trajectory smoother for GEOMETRY ONLY: clean speed v(t), path curvature κ(t), heading,
elevation grade (Z channel), and regime segmentation (Throttle/Brake channels). Do NOT use the acceleration
posterior as the force observable.

Longitudinal segments [t0,t1] in a regime → integral constraint:
  v(t1) − v(t0) = ∫ [ a_drive − a_drag − a_roll − g·sin(grade) ] dt
- COAST (Throttle≈0, Brake=0): v0 − v1 = cr·Δt + ½ρ(CdA/m)·∫v²dt. Known ∫v²dt, Δt → linear in (cr, CdA/m).
  Many coast segments/session → overdetermined, clean.
- FULL-THROTTLE: v1 − v0 = ∫[ T(rpm,gear)/(m·r) − ½ρ(CdA/m)v² − cr ]dt. rpm/gear known per sample →
  ∫(engine basis)dt constrains the engine/power map; drag pinned from coast is subtracted. THE power test.
- BRAKING: v0 − v1 = ∫[ a_brake + a_drag + cr + g·sin(grade) ]dt → braking-grip integral.
LATERAL/grip is KINEMATIC, no integration: a_lat = v²·κ (clean v × geometry κ), NOT the accel posterior.
Friction ellipse: a_long from dv/dt of the CLEAN speed channel (~0.49 m/s), a_lat from v²κ.

Continuity: v shared at segment boundaries (definitional); car params shared across segments + laps. Build
the joint estimator (information form OK) where MEASUREMENTS ARE SEGMENT INTEGRALS with v-derived covariance,
not pointwise a. Propagate honest covariance from the endpoint/speed uncertainties + ∫v²dt uncertainty.

### What to show
1. Per-parameter posterior tightening vs G1 (same 2022 Spain R, same params {m anchored, cr, CdA, C_df, grip
   extents}) — quantify the variance reduction from weak vs strong form.
2. POWER HEADLINE: does the throttle-segment ΔV integral resolve a power/engine-map parameter that F3 could
   not (pointwise)? Report power-envelope + covariance; is it now above the floor for MANY drivers, not 1?
3. Lateral grip from v²κ vs from the accel posterior (F5) — is the v²κ envelope tighter / more consistent?
4. Elevation: does including g·sin(grade) (use a circuit with grade — add 2023 Belgian Q/Spa) improve the
   longitudinal fits vs ignoring it?

### Guardrails (prove-ourselves-wrong)
- Held-out SEGMENT: predict a withheld segment's ΔV from the fitted params; score.
- Posterior-predictive: do fitted params reproduce held-out segment ΔVs within covariance (reduced χ²≈1)?
- Between-lap drift audit (G1 found pointwise filter overconfident ×2.6): does the integral form REDUCE the
  drift overconfidence, or does drift persist (→ real time-varying conditions signal)? Report the factor.
- Honest-null: if weak form does NOT tighten meaningfully, or power still won't resolve, report + diagnose.

### Rules
Dogfood `src.preprocessing.trajectory` for geometry (v, κ, grade, segmentation); honest per-regime ell
(report). Reference G1 `expt-g1/scripts/experiments/g1_*.py` + F-series for patterns. Offline cache
`outputs/cache` (raw streams, never get_telemetry; pos dm, speed km/h); DB `data/f1_data_<year>.db`; sessions
2022 Spain R (vs G1) + 2023 Belgian Q (elevation); `py` not `python`; numpy/scipy only; evidence under
`.agent-work/expt-g2/evidence/`; commit+push as you go; checkpoint smoother fits; FOREGROUND long compute,
NEVER background-and-end-turn (hit E12/F5/F6). Covariance is the referee.

Return: weak-vs-strong tightening per parameter (vs G1); the POWER resolution verdict (integral vs F3's
pointwise null); lateral-grip-from-v²κ vs accel-posterior; elevation effect; drift-overconfidence factor;
held-out + posterior-predictive; ell reported; evidence paths.

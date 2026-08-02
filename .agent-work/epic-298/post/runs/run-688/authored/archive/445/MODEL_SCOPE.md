# Phase-2 Model Scope — coefficient dependencies, intentional decisions (2026-06-13)

User directive: before production, be EXPLICIT about each coefficient's true dependencies and INTENTIONALLY
scope each — model it, model-as-time-varying-state, accept-as-confound (flagged), or ignore (with reason).
"We may choose to ignore the dependency, but let's be intentional." Nothing ignored silently.

Legend: [MODEL] have data + matters + identifiable · [STATE] model as slowly-varying through stint ·
[CONFOUND] cannot separate in our data → accept a contextual readout, flag honestly · [IGNORE] 2nd-order,
intentional · [?] needs the user's ratification (consequential choice).

## Air density ρ  (enters drag, downforce, power)
- depends on: temperature, pressure, humidity, altitude.
- [MODEL] — session weather gives AirTemp/Pressure/Humidity; clean ideal-gas formula; varies a few % and
  multiplies every aero/power term. Already doing it (F2). Cheap, in.

## Drag  CdA  (the single aero force — downforce lumped in; parked)
DRAG MODEL v2 (user-refined 2026-06-13):
  aero force = ½ρ|v_air|²·CdA(θ)·f_follow(gap)·(−v̂_air), decomposed into along-velocity (drag) +
  perpendicular (side force); v_air = v_ground − [v_wind_global(station) + δ_wind(position)].
- [FIRST CUT, tractable now] FREE-AIR SEGMENTATION: clean CdA_freeair measurable only when no car in
  slipstream range ahead (gap > ~1.5-2s, from full-field positions). F2's CdA≈0.94 is CONTAMINATED
  (pooled coast incl. following) — this corrects it. + cr. FOLLOWING as a GLOBAL effect: f_follow(gap),
  single field-shared drag-reduction function, parameterized by gap NOT by who (mirrors grip's global
  track). Free-air anchors f_follow→1.
- [SECOND LAYER, "more impacting"] CdA(θ) — drag as fn of wind/yaw ANGLE (same physics as the side force).
  Identifiable: one lap sweeps many headings vs ~fixed wind → samples θ range. FRAME CALIBRATION (user
  2026-06-13): NOT a hard estimation step — pull `session.get_circuit_info().rotation` from FastF1 (cheap).
  CAVEAT: that rotation is for map-DISPLAY orientation; verify it gives a true compass/wind frame, else
  calibrate the constant offset once vs a known straight's real bearing. ALWAYS pull (don't assume
  year-constant — cheap, avoids silent staleness). Lateral SIDE FORCE falls out of CdA(θ) for free (expect
  SMALL, ~1-2 m/s² vs grip ~30 — near noise, model structurally).
- [THIRD, ambitious] δ_wind(position) LOCAL WIND field — station wind ≠ true local wind (Zandvoort dune
  swirl, windy corners). Weakly identified, confounded with CdA(θ)/terrain. Separating lever = TERRAIN-
  LOCKED deviation REPEATS across sessions while wind DIRECTION changes → fundamentally a MULTI-SESSION ID.
- [MODEL] DRS (discrete Cd switch); air density (have weather). [IGNORE] ride-height/rake (era focus).
- Downforce is lumped into total CdA·v² (induced ∝v²); separate only if 2026 active-aero state modeled.
- OPEN for user: (1) do heading-frame calibration as its own prerequisite step (also fixes F2's wind #)?
  (2) δ_wind is multi-session ID (terrain-repeats vs wind-changes) — agreed?

## Downforce  Cl / C_df  (grip-v², drag)
- DECISION 2026-06-13 (user): DO NOT solve downforce separately. Its only essential role is the grip
  normal-load v²-term, already ABSORBED as k_df in the grip model (GRIP-1/2, fit jointly with μ, works).
  Induced drag is also ∝v² → lumps into total CdA. So a standalone downforce identity buys nothing the
  current goal needs. PARKED-AND-ABSORBED.
- Knowingly given up: Cd/Cl separation + the induced-drag(Cd=Cd0+k_i·Cl²)/DRS bootstrap — capabilities,
  not needs.
- REVISIT TRIGGER: 2026 active aero IS a controllable downforce↔drag tradeoff (sheds downforce to cut
  straight-line drag on a control input). If/when we model the active-aero STATE, downforce returns as its
  own quantity — lumping cannot represent the dual grip+drag effect. Until then, parked.
- depends on (for the record): aero config, DRS, ride-height/rake (ground effect), speed.

## Rolling resistance  cr
- depends on: tyre pressure, tyre temp, compound, load (weight+downforce), surface.
- [IGNORE] temp/pressure variation (2nd-order, small term); note partial collinearity with drag at low
  speed (separates only across a wide speed range — a weak-form identifiability caveat, not a dependency).

## Engine power / torque  T(rpm, gear)
- depends on: rpm (curve shape), engine MODE (team level — the F3 confound), ERS deployment (~160 hp,
  deployed tactically = mode-like), fuel-flow limit (regulated), air density/altitude, temperature.
- DECISION 2026-06-13 (user, POWER-1/2/3): POWER = DEPLOYED-FLOWS, ICE-vs-deploy separation PARKED.
  Deliverables: deployed-power ENVELOPE (relative per-car index, F3-style) + harvest/deploy ENERGY-
  MANAGEMENT profiles (POWER-1 deploy-excess ~90-140 kW; POWER-2 harvest ~50 kW/100-160 kJ/lap). Both
  decoupled, measurable, zero coupling overhead.
  WHY NOT separate ICE: F3 confound (ICE+deploy both add power, no ERS telemetry). The energy-conservation
  bootstrap (harvest+allocation budget constrains total deploy → separates persistent-ICE(rpm) from
  tactical-deploy) was TESTED (POWER-3): the SOC coupling is STABLE (user's integrator-error fear NOT borne
  out — bounded cross-car-consistent offset) BUT NOT WORTH IT — the budget constraint is too loose (harvest
  = noisy lower-bound + engbrake confound; allocation = regulatory max not actual), so it can't cleanly bite,
  and POWER-3's "stability" is necessary-not-sufficient (a consistent BIAS looks the same). No ICE-curve
  recovery demonstrated that beats flows-only. Don't pay the coupling overhead for an unproven separation.
  Also: ICE-vs-deploy attribution is a capability NICETY, not a PREDICTION need (deployed-power + energy
  profile are the on-track signals — like downforce, parked at the right altitude).
  REVISIT TRIGGER: 2026 era (50/50 split makes engine/battery attribution matter + MGU-H removal cleans the
  energy accounting), OR an actual ERS deploy telemetry channel surfaces.
  POWER-1 method note: the lower-envelope trick FAILS for ICE (floor = drag-cruise not engine); ICE would
  need the acceleration regime (high a_long), still deploy-confounded.

## Grip / friction ellipse  (a_lat_max, a_long_max)
- TRUE STRUCTURE (user 2026-06-13): μ_effective = μ_tyre(compound, age, temp) × T_track(circuit surface,
  rubber state, track temp). TWO time-varying pieces pulling OPPOSITE ways — track rubbering-in IMPROVES
  grip, tyre wear DEGRADES it — so naive μ(tyre-age) is their net and can falsely look flat. Plus a
  per-circuit surface constant.
- depends on: compound, tyre temp (cliff outside window), tyre WEAR/age, load≈downforce (v² term), TRACK
  surface (per-circuit const) + rubbering-in (session-global, time-varying) + track temp (measured),
  camber/setup.
- load/speed v² → [MODEL] via N=m·g+downforce·v². compound → [MODEL] (categorical, physics-based, no
  compound_prior wiring). camber/setup → [IGNORE] (per-car const).
- **THE decomposition [STATE, GRIP-2's central problem]:** separate session-GLOBAL T_track(session_time)
  — shared across ALL cars on track, partly anchored by measured track temp — from PER-STINT
  μ_tyre(tyre_AGE, compound). Different indices (wall-clock vs tyre-age) + pit-staggered field = natural
  experiment: cars at different ages/same time → pure tyre; same age/different time → pure track. Requires
  the FLEET (cross-car), not one car. Per-circuit surface = a per-track scale (only for cross-circuit μ).
- WHY this supplants the incumbent: lap-time compound estimation conflates track-rubber + fuel + tyre-deg;
  physics separates all three (track cross-car-shared, fuel=mass anchor, tyre=per-stint-by-age).
- GRIP-1 caveat: its cross-SESSION per-compound μ is "μ_effective on that track that day" (track-
  contaminated), NOT clean tyre μ; within-session isotropy + μ-from-load are unaffected (track const there).

## Mass  m
- depends on: car (reg min), fuel (burns ~linear), driver, ballast, tyre set, damage.
- [MODEL/ANCHOR] reg-min + linear fuel-burn (F4: not fittable, must anchor). ballast/tyre/driver mass →
  [IGNORE] (tiny / constant). damage → [IGNORE] unless flagged (rare exception, like the G1 teammate audit).

## The consequential decisions needing ratification (the [?]s)
1. **Grip time-evolution as a STATE** (tyre/track degradation) — model it (recommended; it's the signal) vs
   treat grip as per-stint constant (simpler). Rec: model as slowly-varying state.
2. **Power = deployed-power, not capability** — accept the mode/ERS confound and ship a contextual power
   index? Or invest in a deployment channel / ERS model to chase capability? Rec: ship deployed-power, flag.
3. **Dirty air / slipstream** in races — prefer quali for clean aero + treat race-drag drift as the
   degradation/traffic signal, vs model traffic explicitly. Rec: quali for clean aero now, model later.
4. **Ride-height/rake aero sensitivity** — the biggest unmodeled aero term on ground-effect cars. Defer
   (accept the bias, flag it) vs attempt a ride-height proxy. Rec: defer, flag.

## RATIFIED 2026-06-13 (user)
- Era focus: TARGET = 2026 split-hybrid (current). Don't over-model ground-effect-era aero (it's the bulk
  of training data + matters, but not the prize). Ride-height/rake → DEFERRED (confirmed). 2026 ~50%
  electric ELEVATES the power/ERS-deployment story.
- Grip μ: ISOTROPY FALSIFIED by GRIP-1 — strongly ANISOTROPIC ellipse, μ_lat > μ_brake > μ_trac (5-14σ;
  braking 54-75% of lateral, traction 26-41%). Envelope = ANISOTROPIC μ·N ellipse ∩ power-cap on traction.
  Model options: μ_lat as the clean per-tyre coefficient + directional ratios (brake/trac), OR a 3-axis
  ellipse. N = m·g + downforce·v²; k_df FIT JOINTLY with μ (GRIP-1: borrowing G1's underabsorbs). CAVEAT
  (verify): braking-below-lateral may be partly a measurement artifact (clean v²κ lateral vs noisier a_long
  clipping peak braking) — cross-check braking via clean speed-channel dv/dt if Speed is ground-derived
  (expt-spdcheck). Traction-lowest is genuine. STATIC μ falsified over a race stint (Spain χ²≈35) → the
  evolution state below is REQUIRED, not optional.
- Grip evolution → STATE, RATIFIED EMPHATICALLY. GOAL: this physics μ(tyre-age) degradation work must
  SUPPLANT the existing (lap-time-based) compound estimation — recover compound ranking + degradation and
  beat the incumbent.
- Power = DEPLOYED-power (mode+ERS confound accepted), confirmed given 2026 electrical split.
- Dirty air → quali for clean aero (confirmed).
- Pacing: work forces ONE AT A TIME. Starting force = GRIP.

## Grip — STATUS (2026-06-13): sufficient starting point reached. Production note (user): compound
prior must be HARVESTED ACROSS MANY SESSIONS (global per-compound μ_fresh + degradation), then
UPDATED LOCALLY per session with track/rubber/temp specifics — a hierarchical global-prior + local-
posterior. Single-session naive is fine for experiments; production = the hierarchical version.
GRIP-3 (deferred): multi-race pooling + tyre-temp (the wear-ordering data limit), then line-resolution.

## Production data-engineering note (user 2026-06-13): RACE-SPECIFIC data store
Build a per-race/per-circuit metadata file (extend the existing race/compound data file) holding all
"facts about this race": track rotation (get_circuit_info), compound data, track-temp trend, per-circuit
surface-grip scale, sector-loop geometry, etc. ALWAYS pull fresh (don't assume year-constant — cheap).
Keeps race facts in one place vs scattered. Production item, not experiment-blocking.

## Scope summary
MODEL: air density, DRS, rpm-shape, v²/load aero+grip, compound, fuel-mass. STATE: grip/track/tyre
evolution. CONFOUND (flagged): engine mode+ERS (→ deployed-power), dirty air (→ quali), ride-height aero.
IGNORE (intentional): rolling temp/pressure, yaw-on-straights, ballast/setup, undeclared damage.

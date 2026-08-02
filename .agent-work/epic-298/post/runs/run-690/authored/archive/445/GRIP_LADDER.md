# Grip force — deliberate single-force build (epic #445 Phase 2)

Priority force (user 2026-06-13): grip is the strongest-resolved channel, where car-vs-driver separation
lives, and the explicit goal is for the physics grip-EVOLUTION model to SUPPLANT the existing lap-time-based
compound estimation. Work it one step at a time. Model = μ·N: N = m·g + downforce(v²) (normal load), μ =
tyre friction coefficient (isotropic first model; envelope = circular μ·N limit ∩ power-cap on traction).

## Methodology (user 2026-06-13): START SIMPLE, chase complexity only at the limit of data utility.
Decided grip model (simple): μ_lat is the clean primary coefficient (clean v²κ); braking/traction = fixed
RATIOS to μ_lat (GRIP-1 ellipse, braking-asymmetry deferred). N = m·g + downforce·v² (k_df fit jointly).
Evolution = GLOBAL track-grip metric (single, ages together, session-time-indexed, shared across all cars)
× PER-STINT per-compound tyre degradation (tyre-age-indexed). Off-line/line-dependence + finer track detail
PARKED. Add complexity (anisotropy detail, line-dependence, tyre-temp, ride-height) only when residuals/
honesty checks show the simple model is insufficient.

## GRIP-2 — Grip evolution: track-vs-tyre decomposition + supplant compound (worktree expt-grip2, branch expt/448-grip2)
Question: using the fleet's pit-staggered tyre ages, can we separate session-global track-grip evolution
from per-stint per-compound tyre degradation — and does the physics tyre-degradation SUPPLANT the existing
(lap-time-based) compound estimation? GRIP-1 falsified static-μ over a race stint (Spain χ²≈35) → this state
is required.

Model (simplest useful): μ_lat_eff(car,lap) = μ_tyre(compound, tyre_age) × T_track(session_time).
- T_track: ONE global multiplier, smooth/low-order in session-time, shared across ALL cars; anchor scale
  (reference lap or measured track-temp trend). Ages together — no line/off-line detail.
- μ_tyre(compound, age): per-compound degradation curve, START low-order (linear-in-age first; add curvature
  only if residuals demand), indexed by TyreLife NOT session-time.
- μ_lat from v²κ / N(v) (peak lateral grip, load-normalized; k_df fit jointly). Braking/traction = deferred
  ratios, not modeled here.
- IDENTIFIABILITY = the whole game: track (session-time index) vs tyre (tyre-age index) separate ONLY because
  pit stops stagger ages — cars at different ages/same time isolate tyre; same age/different time isolate
  track. REQUIRES the fleet (multiple cars, varied pit timing).

Method: 2022 Spain R, ≥6 cars across constructors with VARIED pit timing; tyre compound+age+stint from
FastF1 laps (Compound, TyreLife, Stint); per-lap peak μ_lat; fit the joint two-level model.
Show: (1) separated T_track(session-time) — physically sensible (track greens up)? anchor vs measured track
temp. (2) per-compound μ_tyre(age) degradation curves + SOFT/MEDIUM ranking & rates. (3) identifiability —
is the separation actually RESOLVED (does the pit-stagger give leverage)? report track↔tyre correlation/
covariance — confounded or separated? (4) SUPPLANT comparison — inspect the existing compound estimation
(`src/compound_prior/` + any compound-degradation output/docs/ADRs), compare physics μ_tyre degradation/
ranking to the incumbent; can it supplant? (5) where the SIMPLE model hits its limit (residuals demanding
line-dependence / anisotropy / tyre-temp) → seeds GRIP-3.
Guardrails: held-out car/stint; posterior-predictive; the ×2.6 race drift inflation; honest-null (if track/
tyre don't separate, or degradation isn't resolved above the floor — say so + diagnose).
Rules: dogfood the estimator; ell~10 reported; offline cache; DB; `py`; numpy/scipy; evidence under
`.agent-work/expt-grip2/evidence/`; commit+push; checkpoint fits; FOREGROUND long compute. Covariance referee.

## GRIP-3 — Multi-session compound: hierarchical global-compound + per-race track (worktree expt-grip3, branch expt/448-grip3) [REQUIRED before composing]
Question: pooling grip degradation across MANY races, does the compound WEAR-ORDERING resolve (GRIP-2
single-race was only ~0.5-0.7σ), and does it yield a GLOBAL compound prior (per the production structure:
harvest compound priors across sessions, update locally with track specifics)?

Hierarchical model: μ_lat_eff(race, car, lap) = μ_tyre(compound, age) × T_track[race](session_time).
- μ_tyre(compound, age): GLOBAL across races (same compound ~ behaves alike) — the shared compound prior;
  fresh-μ b_c + degradation g_c per compound, pooled over ALL races. THIS is where the wear-ordering
  resolves (more compounds × conditions × laps).
- T_track[race]: PER-RACE track-greening (each race its own rubbering), session-time-indexed. Local.
- Pit-stagger within each race separates tyre(age) from track(time) [GRIP-2]; pooling races shares g_c.

CRITICAL — KEEP LIGHT (multi-race × full field; per-lap smoother = 16h, would thrash):
- Precompute each CIRCUIT's curvature profile κ(track-position) ONCE (geometric track property, from pooled
  positions — a light spline of heading-change vs arc-length, NOT the full StintSmoother). Cache per circuit.
- Per lap/car: a_lat(t) = v(t)²·κ(s(t)) using the CLEAN SPEED channel + the car's position-along-track s.
  Peak a_lat per lap, load-normalized by N(v)=m·g+k_df·v². NO per-lap trajectory-smoother fits.
- Cache per-race harvests; single bounded run; EVID under THIS worktree; FOREGROUND; never background-end-turn.

Sessions: ~6 races spanning circuits/conditions 2022-2024 (e.g. Spain, Austria, Britain, Belgium, Hungary,
a wet if available) — varied compounds (C1-C5 across races) + pit strategies.

Show: (1) GLOBAL per-compound μ_tyre(age) — fresh-μ + degradation g_c, with the WEAR-ORDERING significance
(does soft>medium>hard wear ladder now resolve at >2σ, vs GRIP-2's ~0.5σ?). (2) per-race T_track curves
(sensible greening each). (3) the global compound prior (b_c, g_c ± cov) = the production-structure
deliverable. (4) supplant check vs src/compound_prior across races. (5) held-out RACE (predict a withheld
race's compound grip from the global prior + that race's track fit). (6) where it still hits limits (tyre-temp).
Guardrails: held-out race; honest-null if wear-ordering still doesn't resolve even pooled (→ needs tyre-temp).
Rules: light extraction (precomputed κ + speed channel); offline cache; DB+FastF1 (Compound/TyreLife/Stint);
`py`; numpy/scipy; commit+push; FOREGROUND single bounded run.

## GRIP-1 — Static grip model: isotropy test + μ-from-load separation (worktree expt-grip1, branch expt/448-grip1)

Question: (1) Is μ ISOTROPIC — load-normalized peak grip equal laterally, under braking, and in low-speed
traction (circular friction limit), or is the ellipse genuinely anisotropic? (2) Can we cleanly separate μ
(tyre coefficient) from N (normal load = m·g + downforce·v²), so μ becomes a clean per-tyre quantity that
GRIP-2 can let evolve?

### Model & method
- Forces from the production estimator: LATERAL a_lat = v²·κ (kinematic — clean v × geometry κ, per the
  weak-form lesson; NOT the raw accel posterior); LONGITUDINAL a_long from the smoother's honest force
  (braking decel, low-speed corner-exit traction). Report ell; note the speed-channel provenance caveat
  (expt-spdcheck pending — if Speed is wheel-derived, braking/traction grip from the speed channel has a
  lockup/wheelspin bias; prefer the position-anchored smoother force for longitudinal where possible).
- Normal load N(v) = m·g + ½ρ·(C_df·A/m... )·v²  → grip ACCEL limit = μ·N/m = μ·(g + downforce·v²/m). Use
  G1's downforce estimate (C_df) and anchored mass; the speed-dependence of the grip envelope (F5 found
  e2>0) should be EXPLAINED by N(v), leaving μ ~flat in v if the model is right.
- At the grip LIMIT (high-utilization samples, the envelope edge), measure peak grip accel per direction;
  divide by N(v)/m to get μ_lat, μ_brake, μ_trac. ISOTROPY TEST: are they equal within covariance?
- Traction: separate the POWER-capped regime (high speed) from the GRIP-capped regime (low-speed corner
  exit) — only the latter measures μ_trac.

### What to show
1. ISOTROPY verdict: μ_lat vs μ_brake vs μ_trac (load-normalized), with covariance — circle or ellipse, and
   by how much. Answers the user's question empirically.
2. μ-from-load separation: does N(v) = m·g + downforce·v² absorb the grip envelope's speed-dependence,
   leaving a ~speed-flat μ? If yes, μ is a clean per-tyre coefficient (the GRIP-2 evolution target). If the
   residual still grows with v, the load model is incomplete (report).
3. Per-compound μ where compounds vary (2022 Spain R has SOFT/MEDIUM) — physics-based, no compound_prior.
4. The power-cap ∩ grip-limit picture on the traction side.

### Guardrails
- Held-out corners/laps; posterior-predictive (does μ·N reproduce held-out peak grip within covariance?).
- Falsify isotropy honestly (if anisotropic, say so + quantify). Falsify the load model (if μ isn't flat in
  v after N-normalization, the model's wrong). Honest-null welcome.

### Rules
Dogfood `src.preprocessing.trajectory`; honest per-regime ell (grip~10, report); offline cache
`outputs/cache` (raw streams, never get_telemetry; pos dm, speed km/h); DB `data/f1_data_<year>.db`; sessions
2023 Belgian Q + 2024 British Q (clean quali envelope) + 2022 Spain R (compounds, traction range); `py` not
`python`; numpy/scipy only; evidence under `.agent-work/expt-grip1/evidence/`; commit+push as you go;
checkpoint smoother fits; FOREGROUND long compute, NEVER background-and-end-turn. Covariance is the referee.

Return: isotropy verdict (μ_lat/brake/trac ± cov, circle vs ellipse); μ-from-load separation result (is μ
speed-flat after N-normalization?); per-compound μ; power-cap vs grip-limit on traction; held-out/posterior-
predictive; ell; evidence paths. This sets the grip MODEL; GRIP-2 = let μ evolve (degradation) + supplant
the compound estimation.

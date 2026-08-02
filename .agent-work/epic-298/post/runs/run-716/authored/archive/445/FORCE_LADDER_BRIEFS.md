# Phase 2 Force-Derivation Ladder (F-series) — explore before implementing

User-authorized overnight exploration (2026-06-13). LAB MODE: no GitHub issues/PRs, no production
module changes; results return to `.agent-work/445/` + branch evidence. Goal (per
PHASE2_DECOMPOSITION_DIRECTION.md): find which car-capability decompositions the honest acceleration
data actually supports — aero (Cd/Cl), engine power (vs mode), vehicle mass (fuel nuisance), grip
envelope — separating car capability from driver skill. Honest-null is a complete result. Build #449
only AFTER the ladder says what's identifiable.

## Common rules (all F-experiments)
- **Dogfood the merged production estimator**: `from src.preprocessing.trajectory import (...)` —
  `enable_cache`, `load_session_offline`, `driver_streams`, `stint_span`, `db_lap_times`,
  `StintSmoother`/`NSStintSmoother`, `fit_stint_hp`, accessors (`acc_at`/`vel_at`/`speed_at`/
  `pos_cov2x2`/`pos_predvar`), `compute_trust_profile`. The estimator gives honest 2D
  acceleration with covariance; derive a_long (along velocity) and a_lat (perpendicular) from the
  velocity+acceleration state. Reference the lab `e10_run`/`e12_run` patterns in the expt-e* worktrees
  if you need a driving example, but use the production API.
- Offline FastF1 cache `C:/Programs/f1Brainz/outputs/cache` (raw streams only, never get_telemetry);
  pos decimetres, speed km/h; DB truth `C:/Programs/f1Brainz/data/f1_data_<year>.db`; weather/RPM/gear
  come from the FastF1 session (car_data has RPM, nGear, Throttle, Brake, DRS; weather via
  session.weather_data). `py` never `python`; numpy/scipy only; commit+push per milestone; checkpoint
  to JSON; foreground long compute, never background-and-end-turn.
- Everything carries covariance — a weak/confounded identification must report a fat covariance and
  say "not separable", not a confident number. The covariance is the referee.
- Sessions: 2022 Spain R (clean race, fuel-burn stint evolution), 2023 Belgian Q + 2024 British Q,
  ≥3 drivers. Use races for mass/stint work, quali for clean single-lap aero where useful.

## F1 — Force-signal regime characterization (worktree expt-f1, branch expt/448-f1)
Question: what does the honest acceleration signal look like, decomposed by driving regime, and
where is each force identifiable? Method: over a session, classify samples into coast /
full-throttle-straight / corner / braking using throttle/brake/curvature; in each regime report the
a_long/a_lat distributions WITH the estimator's covariance, the signal-to-covariance ratio (is the
force resolved above the trajectory uncertainty?), and where each capability lives (drag in coast,
power in throttle, grip in corner/brake). Deliverable: a regime map + per-regime identifiability
verdict — which of aero/power/mass/grip the data resolves and how strongly. Pure characterization,
no fitting of physical params yet.

## F2 — Aero identifiability: drag + downforce (worktree expt-f2, branch expt/448-f2)
Question: can we identify Cd (drag) and Cl (downforce) from honest accelerations, and how much does
wind compensation matter? Method: on coast samples fit -a_long = θ_R + θ_D·ρ·v_air² where v_air is
AIR-relative (use trajectory heading + session wind speed/dir; compare to ground-speed-only fit to
quantify the wind effect). Separate Cd (longitudinal) from Cl/downforce (its signature in how lateral
grip / braking capability grow with v²) via the two channels. Condition on DRS state. Report θ_D, θ_R,
downforce coefficient WITH covariance; the static-across-session assumption check (does pooling the
session tighten it honestly?); and an honest verdict on Cd/Cl separability. Honest-null if the channels
won't separate.

## CROSS-CUTTING (from F1, binding on F4/F5/F6): acceleration observability
Acceleration is weakly observed (honest posterior sd 3-15 m/s²) and its covariance is governed by
the smoother length-scale `ell`, which `fit_stint_hp` leaves loosely pinned (pos/speed chi²≈1 is
blind to accel variance; accel sd ranged 9→372 at identical chi² on one session). THEREFORE every
downstream F-experiment MUST: (a) report the fitted `ell` and the accel covariance it implies;
(b) prefer pooling across the session / many laps to beat the per-sample floor; (c) treat any
single-stint small-force number as covariance-limited; (d) where it matters, sweep `ell` and report
sensitivity rather than trusting one fit. Grip (large forces) is robust to this; aero/power/mass are
covariance-limited.

## F5 — Grip envelope + utilization (worktree expt-f5, branch expt/448-f5) [F1 says grip resolves STRONGLY]
Question: can we measure the friction-ellipse (available grip envelope) from honest accelerations,
and separate available grip (car/compound/conditions) from utilization (driver)? Method: pool
corner + braking + traction samples; in the (a_long, a_lat) plane fit the grip envelope (ellipse /
g-g boundary) per driver/session/compound — its longitudinal extent (braking+traction grip) and
lateral extent (cornering grip), allowing speed/downforce dependence (envelope grows with v²). Then
the utilization signal = how close each sample sits to the fitted boundary (the friction_coupling
utilization idea, fed honest accelerations) → a driver-skill proxy. Compound angle: borrow the
compound-regularizer THINKING but PHYSICS-based (grip = force the tire transmits), NOT lap-time
based, and DO NOT wire `src/compound_prior/` (that's Phase 3) — just note where compounds differ in
the measured envelope if multiple are present. Report: the fitted envelope WITH covariance, per
driver; the available-grip vs utilization split; speed/downforce dependence; and an honest verdict on
whether the envelope is identifiable per session and whether driver utilization separates from car
grip. Honor the cross-cutting accel-observability caveat (report ell, pool). Honest-null welcome.
Sessions: 2023 Belgian Q + 2024 British Q (quali resolves grip best per F1) + 2022 Spain R (race, for
compound/degradation variation), ≥3 drivers.

## F4 — Vehicle mass via fuel-burn nuisance state (worktree expt-f4, branch expt/448-f4)
Question: does the stint-evolution of performance identify the fuel-burn mass slope, breaking the
force/mass degeneracy? Background: F1 says mass is degenerate from a single point (accel=force/mass);
the lever is the DIFFERENTIAL across a race stint — fuel burns ~1.5-2 kg/lap, car gets lighter, so a
force-per-mass observable should rise monotonically through the stint. Method (2022 Spain R only —
the race with real fuel evolution; quali has none): pick an observable that scales as 1/m at fixed
conditions — drag-corrected drive force isn't it (that gives force); instead track the ACHIEVED
acceleration capability at matched conditions across laps (e.g., peak braking decel, or full-throttle
accel at a fixed speed/gear, or corner-exit traction), which scales as F_capability/m(lap). Fit
m(lap)=m_car + m_fuel0 − burn·lap with PRIORS from the rules (min car+driver mass ~798 kg 2022; start
fuel ≤110 kg; burn ~1.5-2 kg/lap) — use F2's drag θ_D≈1.05e-3 (drift-inflated covariance) to correct
drive force where needed. The degeneracy-break test: IF a force coefficient is ~static but the
acceleration capability improves ~linearly through the stint, that linear improvement IS the fuel-mass
slope — fit it and compare to the regulation fuel-burn rate. Honor the cross-cutting accel-observability
caveat (report ell; this is a small-force differential → likely covariance-limited; a relative TREND
may survive even where the absolute force doesn't). Report: the fitted mass slope vs the regulation
expectation WITH covariance; whether it's resolved above the floor; honest-null very possible.

## F6 — Acceleration observability & physical-ell prior (worktree expt-f6, branch expt/448-f6) [THE CRUX]
Question (the Phase-2 methodology crux from F1+F3): acceleration is a LATENT we infer, never measured;
its covariance is prior-dominated by the smoother length-scale ell, which fit_stint_hp leaves loosely
pinned (pos/speed chi²≈1 for short AND long ell; same session accel sd 9→372; only ~1 driver/session
resolves accel). Can we set ell from a PHYSICAL prior on the car's jerk/acceleration bandwidth so the
acceleration covariance is honest, consistent across drivers, and tight enough to unlock the small-force
channels (power/downforce/mass)? Method: (1) Make the dependence crisp — sweep ell on several drivers,
show accel covariance and the "resolved-driver fraction" as functions of ell at fixed pos/speed chi².
(2) Find the information about jerk that DOES exist in the data: longitudinal jerk is constrained by the
speed channel's high-frequency content (how fast speed changes under braking/throttle steps); lateral
jerk by how fast path curvature changes. Estimate the car's actual jerk/acceleration bandwidth from
high-SNR transients (the most-resolved driver, hard braking/throttle events). (3) Derive a
physically-grounded ell (or a jerk-bandwidth prior / acceleration-aware HP target) and re-fit; test
whether power (F3), drag (F2), and grip (F5) identifications become consistent across ALL drivers, not
just the lucky 1. Report: the ell→accel-covariance map; the estimated physical jerk bandwidth + how it
was derived; the proposed acceleration-aware calibration; and whether it unlocks the small-force
channels. This likely DIRECTLY shapes #449's estimator config. Dogfood the production estimator; honor
all common rules. Honest-null (data genuinely can't pin jerk bandwidth → ell must be an assumed physical
constant, document the value + sensitivity) is a complete and important result. Sessions: 2022 Spain R +
2023 Belgium Q, several drivers.

## F3 — Engine power vs mode (worktree expt-f3, branch expt/448-f3)
Question: can we separate the engine's power CAPABILITY (torque-curve shape) from MODE (the level the
team runs)? Method: on full-throttle high-gear straights, drive accel = P/(m·v) − drag − rolling; using
RPM + nGear from car_data, characterize power vs RPM (the curve shape) and test whether a mode-level
shift is separable from the shape across the session (e.g., quali-mode vs race-mode stretches). Report
the power envelope (max observed), the RPM/gear operating-point coverage, and an honest verdict: is
mode de-confoundable from this data, or is the deliverable a power-envelope + a mode-usage signal?
(mass m enters — treat as a known-ish constant here, F4 handles it properly.)

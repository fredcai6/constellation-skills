# Problem Statement — #511 W3 tyre-age grip-evolution + supplant (CAPSTONE)

Delegated/autonomous mode. Reconciled against the frozen launch order
(`511-W3-tyreage.md`), which is the ratified intent. No reachable human; the
Admiral (team-lead) is the human's delegate. Source of truth = LAUNCH_ORDER
Mission / Pre-Rulings / Inherited Context / Inherited Latitude.

## The ask (one bounded issue)

Issue #511, epic #509, tyre-age wave W3 (capstone). Phase-C characterization:
**MEASURED, NOT wired** (no evo wiring — that is Phase-P #450). Four-part
deliverable:

1. **Populate** the empty `race_stint_estimates` table by running the W2 fit
   path over ALL clean 2023 race stints (~889 stints; ~440 driver-races).
2. **Separate** tyre decay `f_tyre(compound, age)` from track evolution
   `g_track`, in a crossed fractional/log-grip model:
   `grip = car_envelope(driver,weekend) + f_tyre(compound, age) + g_track + noise`.
3. **Supplant test**: does physics `μ_tyre(age)` beat the incumbent lap-time
   compound estimators {absolute-C# floor, compound_prior γ}? Neutral
   within-race pairwise-ordering P + magnitude R² + honest covariance overlap.
   #443 empirical sensor (LOO P=0.8032) is an independent CROSS-CHECK, NOT the
   incumbent.
4. **Dashboard + per-axis verdict**: one tyre-age dashboard (coverage map,
   per-axis f_tyre ladders, g_track curves, supplant result, identifiability
   map) + PER-AXIS GO/CONTEXTUAL/NO-GO.

## Verified seams (from source, this worktree, base 0290e419)

- `session_race.load_race_stints(year, gp, driver, *, db_path, store_path=None,
  min_clean_laps=1) -> list[RaceStintData]` — per driver/race; per-lap smoother
  fit (the heavy compute). `RaceStintData` carries ABSOLUTE `tyre_life`,
  `processed_df`, per-lap `mass_kg` (real `race_mass` w/ track_status),
  `cumulative_track_laps` (W3 track-evolution axis), `rho`, `compound`.
- `stint_estimator.estimate_stint(stint, *, k_prior_mu=0.01, k_prior_sigma=0.02,
  n_boot=30, min_samples=20) -> StintEstimate`. Decay model
  `frontier(v,age)=p0·exp(-k·age)+b_aero·v²`, k≥0, MAP prior on k.
  `.lateral_decay` (g0,k,b_aero,3×3 cov) PRIMARY; `.traction_decay`
  (a0,k,b_aero,3×3 cov) SECONDARY; braking/power_drag/coast 2-param completeness.
- `race_stint_store.RaceStintStore(db_path)` (no default path — batch must pass
  one), `.upsert(record)`, `.has(year,gp,driver,stint_num,compound,
  session_type='R')`, `.load(year=None,session_type='R',status=None)->DataFrame`.
  `record_from_stint_estimate(est, session_type='R', fitted_at=None)`,
  `error_record(...)`. Table `race_stint_estimates`, PK
  (year, gp_name, session_type, driver, stint_num, compound); rows carry
  lateral_g0/k/k_sigma/covariance(3×3), traction_a0/k/..., cumulative_track_laps,
  tyre_life_start/end, compound, rho.
- `pooling.py`: `pool_random_effects(values, sigmas)->PooledParameter(mu,
  sigma_mu, tau, ...)`, `fit_drift(values, clock, sigmas)->DriftFit.predict`,
  `fit_two_way(values, teams, circuits)->TwoWayPool(frac_team/circuit/resid,...)`,
  `weighted_trend(...)`. **No within-weekend time term — g_track is NET-NEW.**
- `common.pairwise_ordering.pairwise_ordering_accuracy(cells_df, predicted,
  truth_col, weight_col, race_col="race") -> float` — NEUTRAL (no domain
  imports); the supplant metric.
- `compound_prior.empirical_sensor` (#443) — comparator/cross-check ONLY.
- Quali envelope anchor: `physics_estimates.db` table `session_estimates`.

## Governing constraints (map + launch order)

- `constraint:physics_region_no_evo_import` — `src/physics/` must not import
  evo-region (`evo_predictor`/`latent_power`/`compound_prior`). The SEPARATION
  must stay evo-free. Supplant comparators (C# floor, compound_prior γ, #443)
  are evo-region → consumed via a **neutral boundary by dependency injection**:
  the physics supplant module takes injected incumbent prediction arrays; the
  region-neutral dashboard SCRIPT (scripts/ are not map nodes) reads evo and
  wires them in. (Sanctioned by launch order "comparator via neutral boundary";
  recorded as a decision candidate for reconcile.)
- Anti-circular: physics fit uses STRUCTURAL priors ONLY (monotone-up compound
  ordering, k≥0, plausible ranges) — NO #443 empirical magnitudes. Supplant
  truth (lap-time degradation) is independent of the physics feature (telemetry
  grip decay).
- LOO / held-out for ANY residual/calibration/stability/covariance-honesty
  diagnostic over the pooled (self-weighted) fit (lesson:loo-residual-diagnostic;
  #443 circular-target trap caught via LOO<0.95).
- DB/telemetry-store is the ONLY data source; `py` not `python`.
- 2σ = reference NOT a gate (fine-margin, #512). Measured-not-wired.
- Honest-null is a complete success (per-axis NO-GO valid; lateral primary,
  traction speculative/"a stretch", braking-null expected).
- Physics-region fence: `src/physics/` + store + tests + docs + dashboard
  script + writing `race_stint_estimates` rows. Do NOT couple separation to evo.

## Float triggers (stop conditions) — none active yet

Gate-1 coverage collapse; importing evo into the physics separation; a material
supplant-test reshape; scope beyond physics+store+tests+docs+dashboard; missing
context. Resolved within latitude so far: neutral-boundary injection design,
separate `race_stint_estimates.db` under data/, gate structure.

## Protected intent

The quali five-view path (session_estimator, EstimateStore, session_estimates)
is UNTOUCHED. W2 modules (session_race, stint_estimator, race_stint_store) are
consumed, not modified (unless a defect surfaces — then float). No evo wiring.

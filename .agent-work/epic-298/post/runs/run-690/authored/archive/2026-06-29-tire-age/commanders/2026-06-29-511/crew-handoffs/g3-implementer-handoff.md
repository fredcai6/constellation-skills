# Implementer Handoff — G3 separation (f_tyre vs g_track)

## G2 Coverage Realities (finalized — the store is populated)
Canonical store `C:/Programs/f1Brainz/data/race_stint_estimates.db`: **1,040 stints, all fit_status='ok'**, 20 circuits, 22 drivers. Lateral fit yield 982/1040; **dry lateral 923** (per-compound dry: HARD 369 / MEDIUM 367 / SOFT 187). Traction 988, braking 988, power_drag 972, coast 988. Lateral g0 median 3.17 (range 1.23–5.97), k≥0 on all 982, covariance finite+PSD 982/982. Pit-staggered age span mean 17.6 (max 53); 20/20 races multi-compound. **Raw mean lateral_k already MONOTONE-UP by compound (HARD 0.00294 < MEDIUM 0.00443 < SOFT 0.00553)** — real pre-separation signal.
- **EXCLUDE wet-regime compounds** (INTERMEDIATE 55, WET 3, None 1) from the dry tyre-age separation — different grip regime. Dry SOFT/MEDIUM/HARD only.
- **Mexico is thin** (lateral_fit=4/51, high-altitude de-conflation) — its per-circuit `g_track` is ill-determined; down-weight / flag it (do not let it distort g_track pooling).
- Read-only via `RaceStintStore(...).load(year=2023, session_type='R', status='ok')`.

## Gate
g3 (issue #511 W3 tyre-age capstone). Worktree `C:/Programs/f1Brainz-511`. `py`, never `python`. Suggested model tier: **stronger (Opus-class)** — this is the subtle separation.

## Task
New evo-free module `src/physics/layer2/tyre_separation.py` + `tests/unit/physics/layer2/test_tyre_separation.py`. Separate tyre decay `f_tyre(compound, age)` from track evolution `g_track` over the populated `race_stint_estimates` store (2023), in a crossed log-grip model:

    grip_axis(stint) = car_envelope(driver→constructor, gp, axis)
                       + f_tyre(compound, age)
                       + g_track(gp, cumulative_track_laps)
                       + noise

Per-axis VECTOR: **lateral_mech** (from `lateral_g0`), **lateral_aero** (from `lateral_b_aero`), **traction** (from `traction_a0`/`traction_k`). LATERAL is PRIMARY; traction is SPECULATIVE ("a stretch") — per-axis honest-null is OK and expected for braking/power_drag/coast (do not force them).

`f_tyre(compound, age)` is THE TARGET. Decompose into: a per-compound base offset + a per-compound age-decay rate `k`. The per-stint fit already gives `lateral_g0` (grip at the age reference) and `lateral_k` (decay rate). Produce a **season-pooled per-compound `k`** via `pooling.pool_random_effects` (feed each stint's `lateral_k` + `lateral_k_sigma`), and a per-compound base offset (the residual after removing car_envelope + g_track). Apply a STRONG STRUCTURAL prior ONLY: monotone-up compound ordering (softer compound decays faster: k_SOFT ≥ k_MEDIUM ≥ k_HARD; base grip SOFT ≥ MEDIUM ≥ HARD), k ≥ 0, plausible ranges — via the #496 injectable-(value, sigma) pattern. **NO #443 empirical magnitudes** (anti-circular).

`g_track` = NET-NEW within-weekend track-evolution nuisance on the `cumulative_track_laps` axis, per-(circuit) [one weekend per circuit in 2023], partial-pooled across circuits. `pooling.py` has NO within-weekend time term — build a lightweight one (reuse `pool_random_effects`/`fit_drift` idioms; e.g. a per-circuit slope of grip vs cumulative_track_laps with shrinkage toward a pooled mean). The pit-staggered fleet identifies it: same cumulative_track_laps / different tyre-age → tyre; same tyre-age / different track-state → track.

`car_envelope` = anchored from the QUALI envelope (read `physics_estimates.db` `session_estimates`), NOT re-fit from race noise. Use it as the **RELATIVE per-car anchor** (quali absolute level ~3.2 g differs from race ~2.0 g — center the quali envelope within each session; a global race-vs-quali offset is absorbed by the intercept/per-circuit term, do not force the absolute quali level onto race grip).

## Protected Intent
Phase-C MEASURED-not-wired. No evo wiring. Quali path + W2 modules untouched (read-only).

## Test Mode
Test-after acceptable, but the load-bearing test is a **planted-recovery synthetic**: construct synthetic per-stint inputs with a KNOWN planted f_tyre(compound,age) + g_track + car_envelope; assert the separation recovers them within tolerance; assert the monotone compound prior is enforced; assert evo-free import. Plus a real-data smoke (run on the populated store; report per-compound pooled k + g_track curves + identifiability).

## Close Criteria
- `tyre_separation.py` imports NO evo-region package.
- Per-axis f_tyre vector: lateral_mech (primary), lateral_aero, traction (speculative). Each returns per-compound (base, k) + honest covariance/sigma + n.
- Season-pooled per-compound k via `pool_random_effects` with the monotone structural prior; k ≥ 0.
- g_track is a genuine within-weekend term on `cumulative_track_laps`, per-circuit partial-pooled.
- car_envelope anchored from quali `session_estimates` (relative/centered), mapped driver→constructor via the quali store's `drivers` list.
- **Identifiability diagnostic** reported (how well tyre vs track separate — e.g. the conditioning / variance attributed to each axis; flag aliasing). Use the pit-staggered argument.
- **LOO / out-of-sample** for EVERY residual/stability/covariance-honesty diagnostic over the pooled fit (`lesson:loo-residual-diagnostic`). A self-inclusive diagnostic is blind.
- Planted-recovery synthetic test passes; evo-free; `simplification_limits --paths` clean.

## Allowed Scope
`src/physics/layer2/tyre_separation.py` (new), `tests/unit/physics/layer2/test_tyre_separation.py` (new). Read-only: `race_stint_estimates` store, `physics_estimates.db` session_estimates, `pooling.py`.

## Specific Exclusions
No evo import. No modification of W2 modules / quali path / pooling.py / stores. No #443 empirical magnitudes in the fit. No committed .db.

## Constraints
- `constraint:physics_region_no_evo_import`.
- STRUCTURAL priors only (anti-circular). 2σ = reference NOT a gate.
- LOO for self-weighted-fit diagnostics. Honest covariance. `py` not `python`.

## Verified Seams (re-verify from source)
- `race_stint_store.RaceStintStore(db_path).load(year=2023, session_type='R', status='ok') -> DataFrame`. Columns incl.: `lateral_g0, lateral_k, lateral_k_sigma, lateral_b_aero, lateral_b_aero_sigma, lateral_covariance (3x3 nested list), traction_a0, traction_k, traction_k_sigma, traction_b_aero, traction_covariance, cumulative_track_laps, tyre_life_start, tyre_life_end, n_clean_laps, compound, driver, gp_name, rho, stint_num`. Canonical DB: `C:/Programs/f1Brainz/data/race_stint_estimates.db`.
- `estimate_store.EstimateStore(db_path).load(year=2023, session_type='Q', status='ok') -> DataFrame`. Columns incl.: `constructor, drivers (list of driver codes), gp_name, lateral_mech_grip_g, lateral_mech_grip_g_sigma, lateral_aero_grip_g, lateral_aero_grip_g_sigma, lateral_covariance, traction_accel_ms2, ...`. Quali DB: `C:/Programs/f1Brainz/data/physics_estimates.db`. **Per-CONSTRUCTOR** (race store is per-DRIVER) — map driver→constructor via the `drivers` list for each (year, gp). Lateral is convention-B g-units (SAME space as race `lateral_g0`).
- `pooling.pool_random_effects(values, sigmas, *, sigma_floor=1e-9) -> PooledParameter(mu, sigma_mu, tau, n, q_stat, i2, shrunk, weights)`; `fit_drift(values, clock, sigmas=None) -> DriftFit.predict(clock_target)->(mu,sigma)`; `fit_two_way(values, teams, circuits) -> TwoWayPool(frac_team, frac_circuit, frac_resid, ...)`; `weighted_trend(values, sigmas, times)`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `src/physics/layer2/tyre_separation.py` (new); `pooling.py`; the two stores.
- **Capability:** `purpose:physics_estimation` / `purpose:physics_utilization`.
- **Constraints:** `constraint:physics_region_no_evo_import`; `lesson:loo-residual-diagnostic-over-self-weighted-predictor`.
- **Decision:** `decision:regime_readiness_rubric` (#512) — per-axis vector posture, 2σ reference. Decision pressure (candidate): the W3 crossed log-grip model + net-new g_track term (a new measured axis + pooling structure).
- **Evidence:** planted-recovery; monotone compound ladder; LOO identifiability/stability; honest covariance.

## Required Evidence
1. Planted-recovery test green (paste): recovers planted f_tyre + g_track within tolerance.
2. evo-free assertion (paste).
3. `simplification_limits --paths` clean (paste).
4. Real-data smoke (paste): per-compound pooled k (lateral) with sigma + the monotone ordering; g_track per-circuit slopes; the identifiability diagnostic; LOO stability number.

## Verification Commands
```bash
py -m pytest tests/unit/physics/layer2/test_tyre_separation.py -q
py -m src.utils.simplification_limits --paths src/physics/layer2/tyre_separation.py tests/unit/physics/layer2/test_tyre_separation.py
```

## Authority
Commander decided: model form (crossed log-grip), per-axis vector, lateral primary, structural-priors-only, LOO discipline, car_envelope-from-quali (relative), separate stores. You own: fit mechanics, the g_track lightweight design, prior strengths, pooling structure details, test fixtures. Do NOT decide to import evo, bake #443 magnitudes, modify W2/quali/pooling, or widen scope.

## Stop Conditions
Stop and return if: a non-evo separation is impossible without importing evo; the store coverage cannot support per-compound pooling on the LATERAL axis (coverage-collapse → commander floats); a W2/pooling module must be modified; structural priors are insufficient and only empirical (#443) magnitudes would close it (that is the anti-circular line — STOP).

## Return Format
IMPLEMENTER_RESULT to `C:/Programs/f1Brainz-511/.agent-work/511/crew-handoffs/g3-implementer-result.md`: completed slice, files changed, test mode satisfied, the 4 evidence blocks, the per-axis separation finding (does lateral separate? traction?), assumptions, stop conditions, out-of-scope observations, Workflow Feedback.

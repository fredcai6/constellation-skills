# #513 Phase 4 — FP-session fits: consolidated problem statement (delegated, reconciled vs LAUNCH_ORDER)

## Ask (reconciled against the frozen launch order)
Extend the physics estimator to fit FP sessions, replacing the silent quali-mass fuel bias.
FP is a WEAK car-performance demonstrator but a STRONG driver-utility demonstrator; its main
product feeds Phase 3b (#628, merged), car-capability a heavily-downweighted byproduct.

## Baseline reconciliation (order's assumed baseline vs actual code — source-verified)
- `session_estimator.estimate_session` loads only `"Q"` (`:115` literal) and applies
  `quali_mass(year)` unconditionally (`:125`) → FP fits today are silently fuel-biased. CONFIRMED.
- `estimate_batch.run_estimate_batch` ALREADY threads `session_type` (default `"Q"`); the Q pin
  is only the `estimate_session` internal fallback literal. So the batch driver is FP-ready.
- `mass_model.py` has `quali_mass`/`race_mass`/`fuel_at_lap`; NO `fp_mass` yet. Build target.
- #560 is a SOFT trust profile (`estimate_store_fields._support_trust_profile`), already degrades
  non-Q with reason `practice_session_quali_mass_assumption` — extend, do not add a hard floor.
- #627 explicit-unknown machinery (`normalize_axis_status`/`effective_axis_sigma`/
  `UNRESOLVED_AXIS_SIGMA_FRAC`/`_axis_statuses`) is the reuse target for FP axis status.
- #626 within-session evolution latent (`weekend_state/layer2_evolution.py`) is a documented FLOAT,
  UNWIRED — blocked precisely by missing per-car `cumulative_track_laps` in `session_estimates`
  (this is the Phase-4 Layer-2 unlock the order names).
- #628 `utilization/driver_utility.py` consumes G1 observable rows (v_ideal−v_real per regime),
  reuses `effective_axis_sigma`. FP's product = a car-capability ceiling contribution.

## Data availability diagnostic (planning gate — RESOLVED GREEN)
- FP pos+car telemetry (speed/throttle/brake/gear/drs) present in the store parquet mirror
  (`C:/Programs/f1Brainz/data/telemetry_store_parquet/<sid>/{pos,car}.parquet`), 2018-2026,
  FP1 ~175 / FP2 ~155 / FP3 ~150 sessions. Q baseline present (180).
- FP lap metadata in season `data/f1_data_<year>.db` `lap_times`: compound at 100% coverage,
  plus tyre_life, stint_id, lap_time, valid_lap, track_status. (Compound is OBSERVED, per order.)
- `load_quali_session` is session-type-generic; loading FP is a matter of passing the type.
- VERDICT: the load-bearing held-out gate is runnable on real FP physics fits. Not a proxy-only test.

## The load-bearing falsifiable gate (frozen before numbers — critic F10)
Representativeness is a property of the OBSERVATION (compound, estimated fuel, run-purpose,
track-evolution), NOT the session. Learned observation-property weighting MUST BEAT a
"weight purely by clock-distance-to-Q" baseline on HELD-OUT weekends, else it merely
rediscovered the calendar. A known sandbagging weekend must visibly discount. Honest-null is
a COMPLETE, reportable result — no kill switch.

## Non-circularity contract (grip-anchor → power-residual)
fuel-accounting → fp_mass (independent of any fit); apex grip-class speeds mass-CANCEL → grip
anchor pinned WITHOUT mass/power; power-to-weight extracted from straight/traction classes
SECOND using the grip-pinned CdA + fp_mass. No fit output feeds fp_mass. To be proven explicitly.

## Scope posture (latitude: "do if tractable; float bounded-defer if it balloons")
- CORE (build+test): fp_mass + per-lap latent; representativeness weighting (emergent, not
  hardcoded session weight); the frozen held-out gate harness + sandbagging demo; #627 reuse; #560 extend.
- PRODUCTION WIRING (minimal): parameterize `estimate_session` (session_type + fp_mass).
- UNLOCK: per-car `cumulative_track_laps` into `session_estimates` — aim to land (tractable:
  `compute_cumulative_track_laps` exists); bounded-defer with quantified reason if it balloons.
- #646 full store re-pop across all FP weekends = HEAVIEST compute → bounded demonstration batch
  here, full re-pop handed back as clean follow-on (surface to Admiral).
- Parc-fermé reaction as learnable per-team distribution + weekend process-noise chain = the most
  ambitious arm; carry the chain/process-noise structure, demonstrate the parc-fermé step, and
  bounded-defer a full per-team×season fitted distribution if it balloons.

## user-decision satisfaction (delegated)
Ratified by LAUNCH_ORDER:Mission + What-to-build + Gate. Admiral is ratifying authority.

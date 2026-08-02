# Mission Frame — #513 Phase 4 FP-session fits

## Intent
Make the physics estimator fit FREE-PRACTICE sessions without the silent quali-mass fuel bias,
and produce a per-FP-observation continuous representativeness weighting whose PRIMARY product
feeds Phase-3b driver-utility (#628). The load-bearing, falsifiable claim: observation-property
representativeness beats clock-distance-to-Q on held-out weekends. Honest-null is complete.

## Affected capabilities
- `purpose:physics_estimation` (src/physics) — the five-view per-session estimator + season store.
- Driver-utility (#628 `utilization/driver_utility.py`) — the downstream consumer of FP product.
- Season-store population (`estimate_batch` / `backfill_estimate_store`) — where FP rows would land.

## Structural anchors (source-verified)
- `src/physics/layer2/session_estimator.py` — `estimate_session`: `:115` `"Q"` literal (session load),
  `:125` `m = quali_mass(year)` (unconditional mass). The two seams to parameterize.
- `src/physics/mass_model.py` — `quali_mass`/`race_mass`/`fuel_at_lap`/`race_mass_sigma`;
  `SEASON_BASE_KG`, `DEFAULT_BURN_PER_LAP_KG`, `SC_BURN_FRACTION`. `fp_mass` target lives here.
- `src/physics/apex_extract.py::extract_apex_observations` → `ApexObservation(v_apex,radius_m,a_lat,on_limit)` —
  the mass-robust grip anchor (speed-at-radius; no mass).
- `src/physics/layer2/lateral_view.py::LateralView.fit` — mass-CANCELS to a grip coefficient (mu = |a_lat|/(g cosθ)).
- `src/physics/layer2/estimate_store_fields.py` — #627 `normalize_axis_status`/`effective_axis_sigma`/
  `UNRESOLVED_AXIS_SIGMA_FRAC`/`_axis_statuses`; #560 `_support_trust_profile` (soft, non-Q aware).
- `src/physics/layer2/estimate_store.py` — `EstimateRecord`/`EstimateStore`; PK
  `(year,gp_name,session_type,constructor)`; has `mass_kg_assumed`; NO `cumulative_track_laps`.
- `src/physics/layer2/session_race.py::compute_cumulative_track_laps` — the unlock's existing computation.
- `src/physics/weekend_state/layer2_evolution.py` — #626 within-session evolution latent (FLOAT, unwired;
  blocked by the missing session_estimates `cumulative_track_laps`).
- Season DB `data/f1_data_<year>.db` `lap_times` — per-lap compound (100% coverage), tyre_life, stint_id,
  valid_lap, track_status. Compound is OBSERVED here (join by year/gp/session_type/driver/lap).
- Telemetry store `C:/Programs/f1Brainz/data/telemetry_store.db` + `telemetry_store_parquet/<sid>/{pos,car}.parquet`
  — FP pos+car telemetry present 2018-2026. `estimate_batch` threads `session_type`.

## Governing constraints / assumptions
- physics-region: no evo/fastf1 imports from src/physics; DB is canonical (ORCHESTRATOR_CONTEXT).
- Explicit-unknown contract (OWNER HARD REQ): every FP axis carries resolved/unresolved status;
  unmeasurable → reserved high-σ slot, nothing dropped. Sandbagging → WIDER σ, NEVER bias.
- Nothing binary-dropped: every FP lap earns a weight from its OBSERVATION.
- DB hygiene #632: never commit data/*.db; gitignore scratch DBs.
- Compute #644: single-thread cap ~2x fit time; thread-recovery via OPENBLAS/OMP=4 in detached ENV.

## Decision anchors / decision pressure
- `decision:cross_view_covariance_sparse_representation`, `decision:pooled_sigma_shared_systematic_floor`
  (#627) — reuse, don't fight.
- NEW decision pressure (surface as candidates): (a) fp_mass fuel model (season base + burn·lap-in-stint,
  compound-informed) — a tunable model, must be named/config not hidden; (b) representativeness feature set
  + weighting form; (c) whether per-car cumulative_track_laps lands now or defers; (d) #646 full re-pop
  disposition (bounded demo vs handback); (e) parc-fermé fitted-distribution scope.

## Claims / evidence surfaces
- The frozen held-out gate: learned weighting vs clock-distance-to-Q, held-out weekends, frozen split+rubric.
- Sandbagging-discount demonstration on a known-sandbagging weekend.
- Grip-anchor→power-residual non-circularity proof.
- FP × regime coverage map with σ vs Q baseline.

## Map confidence / staleness
- physics packet: high confidence, source-verified this run. #626 FLOAT status verified in code.
- No stale area blocks the plan; data availability diagnostic done (GREEN).

## Out of scope
- Changing the #644 thread guard (follow-on #650).
- Merging to main (Admiral's).
- Full multi-season store re-pop unless it proves tractable within compute budget (bounded demo default).
- Race/stint mass path (already race_mass).

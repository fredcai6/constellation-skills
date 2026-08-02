# Mission Frame — #563 W2 Race-Fit-Path

Map-first frame for cmdr-563.

## Intent

Generalize the five-view physics estimator from quali-only sessions to RACE stints, producing per-(driver, race, stint) grip-vs-tyre-age observations in a new `race_stint_estimates` store table. Two-phase: Phase 1 diagnoses data viability and floats fit-shape choice (A: per-lap independent, B: joint-decay) to the Admiral; Phase 2 builds the adjudicated shape.

## Affected Capabilities

- `struct:physics.layer2` — cross-session frontier-view estimator; this run extends it to race sessions and adds a decay covariate to the per-session fit concept
- `struct:physics` — mass_model.py (W1, merged); `race_mass` API is the input for per-lap mass correction in race context
- `struct:data` — `TelemetryStore` / `telemetry_session.py`; already stores race sessions (178 R sessions total, 22 for 2023); `read_session(year, gp, 'R')` is the proven entry point
- `struct:sqlite_db` — `f1_data_<year>.db` `lap_times` table; carries `track_status`, `compound`, `tyre_life`, `stint_id` per-lap; `race_stint_estimates` new table to be added

## Examples / Events

- 2023 Bahrain R VER stint 1 (SOFT, 14 clean laps, tyre_life 4–17): fitted cleanly through the existing calibrate_session_hp → fit_lap → smoother_to_processed_telemetry chain
- 2023 full-season coverage: 1,158 total stints, 889 (77%) with ≥10 clean laps; compounds HARD/MEDIUM/SOFT all covered

## Structural Anchors

- `struct:physics.layer2` — `src/physics/layer2/`, module-leaf level; new race-stint loader + estimator land here
- `struct:physics` — `src/physics/`, container; `mass_model.py` (W1 API), `session_fit.py` (quali entry point, NOT modified)
- `struct:data` — `src/data/telemetry_store.py`, `src/data/telemetry_session.py`; DBSession + TelemetryStore read API (existing, untouched)
- `struct:sqlite_db` — `data/f1_data_*.db`; `lap_times` provides `track_status`/`compound`/`tyre_life`; new table `race_stint_estimates` added

## Governing Constraints / Assumptions

- `constraint:physics_region_no_evo_import` — no evo-region imports in `src/physics/` or `src/preprocessing/`; new modules must honor this
- Session-agnostic interface: schema and interface must carry `session_type` + `cumulative_track_laps` so FP/quali can plug in later (FP fitting stays #513)
- `quali_path_untouched`: `session_estimates` table and `EstimateStore` path remain exactly as-is; new table is `race_stint_estimates`, new store class reuses blob encoding from `EstimateStore._cov_list`
- `TrackStatus hard gate` (Admiral ruling): `track_statuses` for `race_mass` MUST come from the real `lap_times.track_status` column — never silently None. GATE MET: column exists with 100% coverage in 2023.
- Data-only: all analysis reads from SQLite DB + TelemetryStore; no direct FastF1 calls from physics

## Decision Anchors & Decision Pressure

- `decision:decoupled_1d_longitudinal` — braking frontier wired for BRAKING only; throttle/coast remain on `clean_longitudinal_from_raw`; race context honors same decision
- `decision:regime_readiness_rubric` — LOO diagnostics required for covariance honesty; any stability diagnostic over a self-weighted predictor must use LOO (lesson:loo-residual-diagnostic-over-self-weighted-predictor)
- **Decision pressure — FIT SHAPE (A vs B, FLOAT POINT)**: Per-stint fitting can follow two shapes:
  - (A) Per-lap independent frontier fits → regress (a_b per lap) vs tyre_age → (g0, k, b_b) + covariance from regression
  - (B) Joint per-stint model: frontier = g0·exp(-k·age) + b_b·v² → fit (g0, k, b_b) directly with age as covariate
  - Evidence: per-lap ~75 braking samples (above _MIN_SAMPLES=20); full stint ~1,050 braking samples. Decay signal ~2-3%/15 laps on SOFT vs per-lap noise TBD. Recommended B (see Phase 1 float) — must be confirmed by Admiral before Phase 2.
- `decision:ideal_lap_sim_two_sided_evaluator` — review trigger fired for W1 (#562); W2 extends mass correction; no new firing expected unless sim path touched

## Claims / Evidence Surfaces

- `claim:lateral_car_prior_boundary_conversion` — car_prior._assemble_lateral is the ONE conversion seam; not touched by W2
- Phase 1 evidence produced (reasoning gate): coverage map, per-lap sample counts, identifiability conditions checked
- Phase 2 evidence required: per-stint frontier fits converge with usable covariance; decay parameter k has bounded sigma; covariance honesty check (LOO over self-weighted predictor if applicable)

## Map Confidence / Staleness / Disputes

- `struct:physics.layer2` — HIGH confidence; recently reconciled for #562 (mass model). The race-session path (load_db_session for 'R') is PROVEN (TelemetryStore has race data; build_db_session works) but NOT yet documented as a physics entry point.
- `tele_car` Parquet `stint=-1` for ALL race samples — this is a STORAGE ARTIFACT (full-session stored, not per-flying-stint). Lap assignment must use `tele_laps.lap_start_time_s`/`lap_end_time_s` time windows. Confirmed working.
- `tyre_life` in `lap_times.tyre_life` starts at 4 for VER Bahrain stint 1 (pre-heated? Installation lap age?). Tyre_life is the correct covariate (FastF1's value), but the "0 age = fresh" mapping may need adjustment. **Flag for Phase 2 implementer**.

## Out of Scope

- `session_estimates` (quali) table — completely untouched
- `compound_prior` / evo region — no imports
- FP session fitting — #513, not this wave
- Race-to-prediction wiring (Phase-P #450) — out of scope
- Cross-session tyre/track separation — W3 (#511), not W2
- `track_statuses` ingestion into TelemetryStore — already present in `lap_times.track_status`, no ingestion needed

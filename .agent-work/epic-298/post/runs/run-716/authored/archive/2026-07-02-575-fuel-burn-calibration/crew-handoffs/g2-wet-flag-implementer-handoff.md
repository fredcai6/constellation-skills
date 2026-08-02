# Implementer Handoff — per-session wet-race flag (data region)

## Gate
`g2-wet-flag` (work-id `575-fuel-burn-calibration`; follow-on to the #575
fuel-mass work — a data-region feature that lets the burn-rate calibration
exclude rain-affected races)

## Task
Extend the existing per-session `session_surface_features` table with a
lightweight, DB-only, all-seasons **wet-race** signal, populate it for the
season DBs, and expose a consumer helper so the physics burn-rate calibration
can flag/exclude wet races. This is the fix for the Silverstone "anomaly":
Silverstone 2024 (24% wet/inter laps) and 2025 (74%) are rain-affected and
should be excluded from a dry-race fuel-burn baseline; a plain dry race like
Spain (0%) is kept.

## Protected Intent
- The existing `session_surface_features.session_rain_flag` column and its
  heavy populator (`weather_features.derive_surface_features_for_event`,
  which reaches an external Open-Meteo API) MUST keep working unchanged. Your
  new light populator must NOT touch `session_rain_flag`, `dry_laps_*`,
  `gap_rain_flag`, or `feature_status` — only the NEW wet columns — so the two
  populators never clobber each other's columns.
- Additive schema change only. Existing DBs must migrate in place without data
  loss, following the existing `_apply_schema_upgrades` pattern.
- Canonical-data constraint: DB-only, no FastF1/Open-Meteo/live calls in the
  new code path. The wet signal is computed purely from `lap_times.compound`.

## Test Mode
Test-first for the pure detection function (hand-computed wet-fraction from a
synthetic lap set); test-after acceptable for the DB plumbing (migration,
upsert, populator) using an in-memory / tmp_path SQLite DB fixture, matching
the convention already used in the data-region tests.

## Close Criteria
1. **Schema extended in BOTH DDL locations** — add three columns to
   `session_surface_features` in `src/data/schema.sql` AND the mirrored
   `CREATE TABLE` in `src/data/database/_core.py`:
   - `wet_lap_count INTEGER` — # laps on WET or INTERMEDIATE compound
   - `total_lap_count INTEGER` — # laps in the race session (denominator)
   - `wet_lap_fraction REAL` — wet_lap_count / total_lap_count (NULL if no laps)
2. **Idempotent migration** — extend `_core.py::_apply_schema_upgrades` to
   `ALTER TABLE session_surface_features ADD COLUMN ...` for each new column,
   guarded by a `PRAGMA table_info(session_surface_features)` existence/columns
   check (the table may not exist yet on a brand-new DB — in that case skip and
   let `executescript` create it with the new columns; only ALTER when the
   table exists but lacks the column). Follow the exact shape of the existing
   `sessions`-table migration block right above it.
3. **Non-clobbering upsert** — add a `DatabaseManager` method (e.g.
   `upsert_session_wet_features(session_id, wet_lap_count, total_lap_count,
   wet_lap_fraction)`) in `src/data/database/_ingest.py` that uses
   `INSERT INTO session_surface_features (session_id, wet_lap_count,
   total_lap_count, wet_lap_fraction) VALUES (...) ON CONFLICT(session_id) DO
   UPDATE SET wet_lap_count=excluded.wet_lap_count, ...` — i.e. it creates the
   row if absent (other columns NULL) or updates ONLY the wet columns in place,
   never touching session_rain_flag / dry_laps_* / gap_rain_flag /
   feature_status. Do NOT reuse the existing `INSERT OR REPLACE`
   `upsert_session_surface_feature` (that replaces the whole row and would
   clobber the dry-surface columns).
4. **Pure detection function** — a function that, given a session's lap
   compounds (or a `DatabaseManager` + session_id), returns
   `(wet_lap_count, total_lap_count, wet_lap_fraction)` counting laps whose
   compound is WET or INTERMEDIATE (case-insensitive), consistent with the
   WET/INTERMEDIATE criterion already in
   `weather_features.py::_session_rain_flag`. Put it in
   `src/data/weather_features.py` next to `_session_rain_flag` (cohesion), and
   reuse `DatabaseManager.get_lap_times(session_id=...)` to read compounds.
5. **All-seasons populator + CLI** — a populator that iterates race ('R')
   sessions in a season DB and upserts the wet columns for each, plus a
   runnable `scripts/populate_wet_features.py` that runs it over
   `data/f1_data_{year}.db` for a given year (or a default 2019-2026 sweep).
   Idempotent, resumable, timestamped progress logging, DB opened read-write
   only for the target season DB. Run it against the real season DBs
   2019-2026 and report coverage.
6. **Physics consumer helper** — in `src/physics/burn_rate_calibration.py`,
   add a small read-only helper (e.g.
   `session_wet_fraction(year, gp_name, lap_times_db_path) -> Optional[float]`)
   that reads the stored `session_surface_features.wet_lap_fraction` for the
   race session (returns None if the column/row is absent). Then add an
   `exclude_wet` path to the validation script
   `scripts/validate_burn_rate_hypothesis.py`: when a race's wet_lap_fraction
   exceeds a named threshold (default 0.05 — a small module-level constant,
   not a magic literal), mark it WET in the PRIMARY ceiling table and exclude
   it from any summary stats, printing the wet fraction. Do NOT change
   `mass_model.py`. Keep the physics side reading the STORED value (the point
   is the flag lives in the DB); do not recompute compounds inside physics.
7. **Tests** (`tests/unit/` under the appropriate data + physics dirs):
   - detection function: hand-computed fractions (all-dry -> 0.0; mixed ->
     count/total; all-inter -> 1.0; empty -> None fraction).
   - migration: an old-schema `session_surface_features` (without the new
     columns) gains them after `_apply_schema_upgrades`, idempotently
     (running twice is a no-op), and existing rows keep their old column
     values (session_rain_flag etc. preserved).
   - non-clobbering upsert: writing wet columns then reading back leaves a
     pre-existing `session_rain_flag`/`feature_status` on the same row intact;
     and a fresh row gets wet columns with the others NULL.
   - physics consumer: `session_wet_fraction` returns the stored value / None
     when absent (synthetic tmp DB).
8. **Verification** — the real-data populate run reproduces this known table
   (compute-only, already checked): Spain 2023/24/25 = 0.0; Silverstone
   ('Great Britain') 2023 = 0.0, 2024 ~0.24, 2025 ~0.74; Monaco 2023 ~0.29,
   2024/25 = 0.0. Report the actual populated values.

## Allowed Scope
- `src/data/schema.sql`, `src/data/database/_core.py`,
  `src/data/database/_ingest.py`, `src/data/weather_features.py`
- `scripts/populate_wet_features.py` (new)
- `src/physics/burn_rate_calibration.py` (add the read-only consumer helper
  only), `scripts/validate_burn_rate_hypothesis.py` (add the exclude-wet path)
- `tests/unit/...` (new tests), and the real `data/f1_data_{year}.db` files
  (populate the wet columns — this is the intended data write)

## Specific Exclusions
- Do NOT modify `src/physics/mass_model.py`.
- Do NOT modify the pre-existing untracked scratch scripts
  (`scripts/mass_validation_dashboard.py`, `mass_fuel_dashboard.py`,
  `bahrain_frontier_validation.py`, `build_lateral_load_cache.py`,
  `lateral_load_unitization.py`, `tyre_age_overview.py`,
  `tyre_degradation_validation.py`).
- Do NOT change `session_rain_flag` semantics or the heavy
  `derive_surface_features_for_event` path.
- Do NOT add a FastF1 or Open-Meteo call anywhere in the new code.

## Constraints
- `py` (not `python`) for all commands. Python launcher, Python 3.14.
- DB-only; canonical data source constraint.
- `py -m src.utils.simplification_limits --paths <touched files>` must pass
  (note the required `--paths` flag).
- Follow the existing migration idiom in `_core.py::_apply_schema_upgrades`
  exactly (PRAGMA table_info + conditional ALTER).

## Map Anchors (inbound)
- **Structural:** `struct:data` — `src/data/schema.sql`,
  `src/data/database/{_core,_ingest}.py`, `src/data/weather_features.py`
  (existing `_session_rain_flag`, `session_surface_features` table).
  `struct:physics` — `src/physics/burn_rate_calibration.py` (read-only
  consumer of the stored per-session flag).
- **Capability:** new per-session wet-race signal (graded wet_lap_fraction)
  in the canonical DB; consumed by the fuel-mass calibration to exclude
  rain-affected races.
- **Constraints/assumptions:** canonical-data (DB-only); data/physics regions
  stay distinct — physics reads the stored flag via the DB (DB-mediated, no
  new import coupling), it does not import the data-region populator.
- **Evidence expectations:** the known wet-fraction table above (Silverstone
  2024/2025 wet, Spain dry, Monaco 2023 wet) must reproduce.

## Required Evidence
- `py -m pytest <new test paths> -q` output.
- Output of `py scripts/populate_wet_features.py` over 2019-2026 (coverage +
  the verification values).
- Output of `py scripts/validate_burn_rate_hypothesis.py` showing wet races
  now flagged/excluded in the PRIMARY ceiling section.
- `py -m src.utils.simplification_limits --paths <files>` PASS.

## Verification Commands
```bash
py -m pytest tests/unit/data tests/unit/physics/test_burn_rate_calibration.py -q
py scripts/populate_wet_features.py
py scripts/validate_burn_rate_hypothesis.py
py -m src.utils.simplification_limits --paths src/data/weather_features.py src/data/database/_ingest.py src/data/database/_core.py scripts/populate_wet_features.py src/physics/burn_rate_calibration.py scripts/validate_burn_rate_hypothesis.py
```

## Suggested Model Tier
Stronger — reason: rigorous data-region schema/migration change with a
non-clobbering-upsert subtlety and a cross-region (data->physics) consumer;
correctness of the migration idempotency and the ON CONFLICT upsert matters.

## Authority
Design is settled (do not re-litigate): extend the existing table (not a new
table); graded `wet_lap_fraction` + supporting counts; light populator owns
ONLY the new columns via ON CONFLICT DO UPDATE (leaves session_rain_flag to
the heavy pipeline); detection from lap_times compounds (WET/INTERMEDIATE);
physics reads the stored value; default exclude threshold 0.05 as a named
constant. If you find the ON CONFLICT upsert can't preserve other columns as
specified, STOP and report rather than falling back to INSERT OR REPLACE.

## Stop Conditions
Stop and return if: the migration can't be made idempotent within the
existing pattern; the ON CONFLICT upsert would clobber sibling columns; a
season DB is structurally different enough that the populator can't run; a
decision beyond this handoff's authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode
satisfied, evidence (paste the populated wet-fraction values and the updated
validation ceiling table), assumptions, stop conditions hit, out-of-scope
observations, workflow feedback.

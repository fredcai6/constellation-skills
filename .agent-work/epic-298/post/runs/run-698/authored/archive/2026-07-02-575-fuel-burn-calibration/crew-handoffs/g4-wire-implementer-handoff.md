# Implementer Handoff — DB-stored per-session burn rate + resolver + wiring (g4)

## Gate
`g4-wire` (work-id `575-fuel-burn-calibration`). Stores the calibrated
per-(season, circuit) dry burn rate per-session in the canonical DB, adds a
runtime resolver, and WIRES the live physics consumer (`session_race.py`) to
inject it into `race_mass` via the `burn_per_lap_kg` seam added in g3. This is
the change that makes the mass model actually USE the clean baseline.

## Prerequisite (already landed)
g3 added to `src/physics/mass_model.py`: `MAX_FUEL_KG_BY_SEASON` /
`max_fuel_for_season`, and optional `burn_per_lap_kg` (+ `max_fuel_kg` on
`fuel_at_lap`) params whose defaults reproduce prior behavior. Do NOT re-open
mass_model.py here except to READ it.

## Task
1. **Store** a per-session calibrated dry burn rate in a new derived table
   `session_fuel_features`.
2. **Populate** it for all race sessions 2019-2026 (dry races measured via the
   throttle-integral; wet races skipped, per the wet flag from g2).
3. **Resolve** a burn rate for any (year, gp) with a graceful fallback chain
   that returns the global default when the DB is unpopulated (so existing
   unit tests on synthetic DBs are UNAFFECTED).
4. **Wire** `session_race.load_race_stints` to resolve + pass `burn_per_lap_kg`
   to `race_mass`.

## Protected Intent — CRITICAL backward-compat property
The resolver MUST return `mass_model.DEFAULT_BURN_PER_LAP_KG` (1.8) when the
target DB has NO populated `session_fuel_features` data for that season. Reason:
`race_mass(..., burn_per_lap_kg=1.8)` is byte-identical to
`race_mass(..., burn_per_lap_kg=None)` (default is also 1.8). So on the
synthetic DBs used by `tests/unit/physics/layer2/test_session_race.py` (which
have no fuel-feature rows), the wiring is a NO-OP and every existing session_race
test — including `test_mass_kg_values_match_race_mass`, which recomputes
`race_mass` with defaults — MUST still pass UNCHANGED. Verify this explicitly.
The numeric change happens ONLY against the real populated season DBs (the
intended, user-acknowledged live change to the W3 tyre-age path). Stored
artifacts (`race_stint_estimates.db`) are re-batched separately (deferred) — do
NOT re-run any estimate/stint batch here.

## Test Mode
Test-first for the resolver's fallback chain (pure over a tmp DB) and the pure
detection/aggregation; test-after acceptable for the populator plumbing. Verify
the session_race no-op property with an explicit test.

## Close Criteria
1. **Schema** — new derived table in BOTH `src/data/schema.sql` AND the mirrored
   `CREATE TABLE` in `src/data/database/_core.py`:
   ```sql
   CREATE TABLE IF NOT EXISTS session_fuel_features (
       session_id INTEGER PRIMARY KEY,
       est_burn_kg_per_lap REAL,   -- dry throttle-integral mean; NULL if wet/uncomputable
       n_laps_used INTEGER,        -- laps contributing to the estimate
       source TEXT,                -- 'measured' | 'wet_skipped' | 'no_telemetry'
       FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
   );
   ```
   No migration entry is needed in `_apply_schema_upgrades` for a brand-new
   table (the `CREATE TABLE IF NOT EXISTS` in schema.sql handles fresh + existing
   DBs since the table is new) — BUT confirm existing DBs get it: since
   `_init_database` runs `executescript(schema.sql)` on every `DatabaseManager`
   init, the `IF NOT EXISTS` create will add it to existing DBs. Verify by
   opening a real season DB via DatabaseManager and checking the table exists.
2. **DatabaseManager accessors** in `src/data/database/_ingest.py`:
   `upsert_session_fuel_features(session_id, est_burn_kg_per_lap, n_laps_used,
   source)` (INSERT ... ON CONFLICT(session_id) DO UPDATE of these columns) and
   `get_session_fuel_features(session_id=None) -> pd.DataFrame`, mirroring the
   existing `upsert_session_wet_features` / `get_session_surface_features`
   idioms.
3. **New physics module** `src/physics/fuel_features.py` (keep
   `burn_rate_calibration.py` unchanged — it is near the 999-line file cap):
   - `populate_fuel_features_for_db(year, *, db_path, store_path=None,
     wet_threshold=WET_EXCLUDE_THRESHOLD)` — iterate race ('R') sessions in the
     season DB; for each, read the wet fraction (reuse
     `burn_rate_calibration.session_wet_fraction`); if wet (>= threshold) upsert
     `source='wet_skipped'`, est NULL; else compute
     `burn_rate_calibration.season_burn_rate_estimate(year, gp, store_path=...)`
     and upsert `est_burn_kg_per_lap`, `n_laps_used`, `source='measured'`
     (or `'no_telemetry'` with est NULL if the estimate is None). Idempotent,
     timestamped progress logging. Uses `DatabaseManager` for writes.
   - `resolve_race_burn_rate(year, gp, *, db_path) -> tuple[float, str]` —
     returns `(burn_kg_per_lap, source)` with this EXACT fallback order:
     1. the (year, gp) session's stored `est_burn_kg_per_lap` where
        `source='measured'` and est is not NULL -> `(value, 'session')`.
     2. else the mean of that DB's `source='measured'` est values (season mean,
        same DB) -> `(mean, 'season_mean')`.
     3. else `(mass_model.DEFAULT_BURN_PER_LAP_KG, 'global_default')`.
     Read-only (`mode=ro`); tolerate a missing table/rows by degrading to
     step 3 (so an unpopulated DB yields the global default — the no-op
     property above).
   - The module imports from `burn_rate_calibration` (physics) and
     `mass_model` (physics) and `src.data.database` (DatabaseManager). No evo,
     no fastf1.
4. **CLI** `scripts/populate_fuel_features.py` — run
   `populate_fuel_features_for_db` over 2019-2026 (default) or a `--year`.
   Print coverage + the resolved per-(season, circuit) values for the four
   reference circuits (Bahrain / Spain(-or-Barcelona-Catalunya) / Great Britain
   / Monaco) so the result can be eyeballed.
5. **Wire `session_race.load_race_stints`** (`src/physics/layer2/session_race.py`):
   resolve the burn rate ONCE per `(year, gp)` at the top of the load (call
   `fuel_features.resolve_race_burn_rate(year, gp, db_path=db_path)`), and pass
   `burn_per_lap_kg=<resolved>` into the `race_mass(...)` call (the real call
   site around line ~608; the other `race_mass` mentions at ~75/107 are
   docstring/comments — update the docstring to note the burn rate is resolved,
   but there is ONE real call). Keep `track_statuses=all_track_statuses` (the
   hard gate) intact. Import `resolve_race_burn_rate` at module top;
   `session_race` already reads the DB so this stays within-region.
6. **Populate the real DBs** — run the CLI over 2019-2026 and report the
   populated/resolved values. Expected shape: dry circuits get their measured
   rate (Bahrain ~1.72, Spain ~1.47, Great Britain dry-year ~1.79, Monaco dry
   ~1.0); wet races (Great Britain 2024/2025, Monaco 2022/2023) resolve to the
   season mean (not their own wet value).
7. **Tests**:
   - `tests/unit/physics/test_fuel_features.py` — resolver fallback chain
     (session hit; season-mean; global default on empty DB — all on tmp DBs);
     populator marks a wet session `wet_skipped` and a dry one `measured`
     (synthetic DB + mocked `season_burn_rate_estimate`/`session_wet_fraction`).
   - data test for `upsert_session_fuel_features` / `get_session_fuel_features`
     (non-clobbering ON CONFLICT; round-trip) under `tests/unit/data/`.
   - a session_race no-op test: on the existing synthetic DB fixture,
     `load_race_stints` produces the SAME `mass_kg` as before wiring (i.e.
     `test_mass_kg_values_match_race_mass` stays green unchanged — run the
     existing suite to confirm).
8. Verification commands (below) all pass; `simplification_limits --paths` PASS
   on every touched/new file.

## Allowed Scope
- `src/data/schema.sql`, `src/data/database/_core.py`,
  `src/data/database/_ingest.py`
- NEW `src/physics/fuel_features.py`, NEW `scripts/populate_fuel_features.py`
- `src/physics/layer2/session_race.py` (wire the resolver in; minimal)
- NEW `tests/unit/physics/test_fuel_features.py`, new data test file (or extend
  an existing data test module)
- the real `data/f1_data_{year}.db` files (populate the fuel-features rows)

## Specific Exclusions
- Do NOT modify `src/physics/mass_model.py` (g3 is done) or
  `src/physics/burn_rate_calibration.py` (at the line cap — the new module
  imports from it).
- Do NOT re-run any estimate/stint batch populator
  (`estimate_batch`/`race_stint_batch`/`fit_batch`) — stored-artifact re-batch
  is a separate deferred follow-up.
- Do NOT modify the pre-existing untracked scratch scripts.
- Do NOT weaken any existing test assertion. If wiring breaks
  `test_mass_kg_values_match_race_mass`, STOP — it means the no-op property is
  violated; fix the resolver's default fallback, don't edit the test.

## Constraints
- `py` (not python). DB/telemetry-store only; no fastf1/evo imports.
- Region layering: `session_fuel_features` schema + accessors in data; the
  computation/resolver in physics (physics may import data — data is the bottom
  layer — but data must NOT import physics).
- Backward-compat no-op property (Protected Intent) is the top constraint.
- `simplification_limits --paths` must pass (new module under 999 lines;
  functions under 100).

## Map Anchors (inbound)
- **Structural:** `struct:data` (`schema.sql`, `database/{_core,_ingest}.py` —
  new `session_fuel_features` table + accessors); `struct:physics` (new
  `fuel_features.py`; reads `burn_rate_calibration` + `mass_model`);
  `struct:physics.layer2` (`session_race.py` — the wired live consumer).
- **Capability:** physics mass/fuel accounting now injects the calibrated
  per-(season, circuit) burn rate into `race_mass` on the live W3 race-stint
  path.
- **Constraints:** `constraint:physics_region_no_evo_import`; mass_model stays
  DB-free (the resolver, not mass_model, reads the DB); data does not import
  physics.
- **Decision anchors:** `decision:burn_rate_calibration_design` — per-(season,
  circuit), DB-stored, injected via the g3 override seam.
- **Evidence expectations:** existing `test_session_race.py` green UNCHANGED
  (no-op property); resolver fallback chain tested; real populate reproduces
  the reference circuit rates.

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_session_race.py tests/unit/physics/test_fuel_features.py tests/unit/data -q` (existing session_race green unchanged + new green).
- Output of `py scripts/populate_fuel_features.py` (coverage + resolved reference-circuit rates; show a wet race resolving to season_mean and a dry race to its session value).
- `py -m src.utils.simplification_limits --paths <all touched/new files>` PASS.
- A short before/after: pick ONE real (year, gp, driver) dry case, show `load_race_stints` `mass_kg[0]` with the flat 1.8 default vs the resolved calibrated rate (the intended live delta), to confirm the wiring actually changes real output.

## Verification Commands
```bash
py -m pytest tests/unit/physics/layer2/test_session_race.py tests/unit/physics/test_fuel_features.py tests/unit/data -q
py scripts/populate_fuel_features.py
py -m src.utils.simplification_limits --paths src/data/schema.sql src/data/database/_core.py src/data/database/_ingest.py src/physics/fuel_features.py scripts/populate_fuel_features.py src/physics/layer2/session_race.py tests/unit/physics/test_fuel_features.py
```
(Note: `simplification_limits` only checks `.py` files; drop `schema.sql` from
that command if it errors on the non-Python path.)

## Suggested Model Tier
Stronger — touches a closed epic's live path (`session_race`), a new DB table +
accessors, a resolver with a subtle backward-compat no-op property, and a
cross-region (physics->data) populator. Correctness of the fallback chain and
the no-op property is critical.

## Authority
Settled: new `session_fuel_features` table; measured-dry / wet-skipped;
resolver fallback session -> season_mean -> global default (1.8); wire only
`session_race` (committed consumer); no cross-year circuit fallback in this
gate (season_mean is the wet-race fallback — note cross-year rescaled fallback
as a future refinement in the result). If the no-op property can't hold, STOP
and report.

## Stop Conditions
Stop and return if: the no-op property breaks an existing session_race test;
the region layering would force data to import physics; a batch re-run seems
required; a decision beyond this handoff is needed.

## Return Format
IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied,
evidence (populate output + reference rates + the before/after live delta +
test counts), assumptions, stop conditions, out-of-scope observations,
workflow feedback.

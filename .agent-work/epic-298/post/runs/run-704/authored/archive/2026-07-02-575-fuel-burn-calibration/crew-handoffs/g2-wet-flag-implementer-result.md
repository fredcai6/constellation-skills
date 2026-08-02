# Implementation Result — g2-wet-flag

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2-wet-flag` (work-id `575-fuel-burn-calibration`) — per-session graded wet-race
signal in the canonical DB, consumed by the fuel-burn calibration to exclude
rain-affected races.

## Completed slice
Full handoff implemented end-to-end:
1. Extended `session_surface_features` with `wet_lap_count INTEGER`,
   `total_lap_count INTEGER`, `wet_lap_fraction REAL` in BOTH DDL locations.
2. Idempotent additive migration for pre-existing DBs (PRAGMA-guarded ALTER,
   skips a brand-new DB where CREATE already includes the columns).
3. Non-clobbering `upsert_session_wet_features` (`ON CONFLICT(session_id) DO
   UPDATE` of the wet columns only) — never touches `session_rain_flag` /
   `dry_laps_*` / `gap_rain_flag` / `feature_status`.
4. Pure detection function `session_wet_lap_features` (DB-only, WET/INTERMEDIATE
   case-insensitive, next to `_session_rain_flag`).
5. All-seasons populator (`populate_wet_features_for_db`) + runnable
   `scripts/populate_wet_features.py` (default 2019–2026 sweep, idempotent,
   resumable, timestamped logging). Ran it against the real season DBs.
6. Physics read-only consumer `session_wet_fraction(year, gp_name,
   lap_times_db_path)` reading the STORED value, named threshold
   `WET_EXCLUDE_THRESHOLD = 0.05`, and an exclude-wet path in
   `scripts/validate_burn_rate_hypothesis.py` (marks WET + excludes from the
   dry-baseline summary, prints the wet fraction). `mass_model.py` untouched.
7. New tests for detection, migration, non-clobbering upsert, populator, and the
   physics consumer.

## Scope
**Files changed:**
- `src/data/schema.sql` — 3 wet columns on `session_surface_features`.
- `src/data/database/_core.py` — mirrored DDL + idempotent migration, extracted
  into `_ensure_session_surface_features(conn)` (create + guarded ALTER).
- `src/data/database/_ingest.py` — `upsert_session_wet_features` (ON CONFLICT,
  wet columns only).
- `src/data/weather_features.py` — `session_wet_lap_features` (detection) +
  `populate_wet_features_for_db` (populator).
- `scripts/populate_wet_features.py` — NEW CLI populator.
- `src/physics/burn_rate_calibration.py` — `WET_EXCLUDE_THRESHOLD` +
  read-only `session_wet_fraction`.
- `scripts/validate_burn_rate_hypothesis.py` — exclude-wet path in the PRIMARY
  ceiling table.
- `tests/unit/data/test_wet_features.py` — NEW (13 tests).
- `tests/unit/physics/test_burn_rate_calibration.py` — +1 class (6 wet tests).
- `data/f1_data_2019.db` … `data/f1_data_2026.db` — intended data write (wet
  columns populated for 167 race sessions).

**Specific exclusions touched:** no — `src/physics/mass_model.py` untouched
(`git diff --stat` empty); all 7 pre-existing untracked scratch scripts remain
`??` and unmodified; no FastF1/Open-Meteo call added anywhere.

## Behavior changed
Yes. A graded per-session wet-lap fraction now lives in the canonical DB and the
fuel-burn validation excludes rain-affected races from the dry-race baseline. The
heavy `derive_surface_features_for_event` / `session_rain_flag` path is unchanged
(existing `tests/unit/test_weather_features.py` all still pass).

## Map Impact
- **Structural anchors touched:** `struct:data` —
  `src/data/schema.sql`, `src/data/database/{_core,_ingest}.py`,
  `src/data/weather_features.py`: new wet columns on `session_surface_features`,
  a non-clobbering wet-only upsert, and a DB-only detection + populator beside
  `_session_rain_flag`. `struct:physics` —
  `src/physics/burn_rate_calibration.py`: a read-only, DB-mediated consumer of
  the stored flag (no new import coupling to the data-region populator).
- **Capabilities added:** per-session graded `wet_lap_fraction` in the canonical
  DB; consumed by the fuel-mass calibration to exclude rain-affected races.
- **Constraints/assumptions honored:** canonical-data (DB-only, no
  FastF1/Open-Meteo in the new path); data↔physics stay distinct (physics reads
  the STORED value through a read-only SQLite query, does not recompute
  compounds or import the populator).
- **Claims/evidence produced:** the known wet-fraction table reproduces exactly
  (see Evidence) — Silverstone 2024/2025 wet, Spain dry, Monaco 2023 wet.
- **Triage candidates:** `_apply_schema_upgrades` in `_core.py` was already over
  the 100-line simplification limit before this change (see Out-of-scope).

## Test mode
**Required:** test-first for the pure detection function; test-after for the DB
plumbing (migration / upsert / populator) and the physics consumer.
**Satisfied:** yes. Detection tests were authored first (hand-computed
fractions). Note: because the single new data test file imports symbols from
several gates, the detection test could not be *collected* in isolation until the
sibling symbols existed, so the first observed run of the detection tests was
green rather than a standalone red — the detection logic is pure and
hand-verified. DB-plumbing and consumer are test-after as specified.

## Evidence

### New tests
```bash
py -m pytest tests/unit/data/test_wet_features.py tests/unit/physics/test_burn_rate_calibration.py -q
```
**Result:** pass — `72 passed` (13 new wet-feature + 59 burn-rate incl. 6 new
wet-consumer).

Broader no-regression sweep (includes the untouched heavy pipeline tests):
```bash
py -m pytest tests/unit/data tests/unit/physics/test_burn_rate_calibration.py tests/unit/test_weather_features.py -q
```
**Result:** pass — `178 passed` (existing `test_weather_features.py` 10/10 green
→ heavy `session_rain_flag` path unaffected).

### Populator over the real 2019–2026 DBs
```bash
py scripts/populate_wet_features.py
```
**Result:** pass — `167 race session(s) populated across 8 season(s)`, idempotent
on re-run. Verification values (STORED and read back from the DBs) reproduce the
handoff's known table exactly:

| year | circuit         | wet_lap_count | total_lap_count | wet_lap_fraction | expected |
|-----:|-----------------|--------------:|----------------:|-----------------:|---------:|
| 2023 | Spain           | 0             | 1312            | 0.000            | 0.0      |
| 2024 | Spain           | 0             | 1310            | 0.000            | 0.0      |
| 2025 | Spain           | 0             | 1203            | 0.000            | 0.0      |
| 2023 | Great Britain   | 0             | 971             | 0.000            | 0.0      |
| 2024 | Great Britain   | 234           | 960             | 0.244            | ~0.24    |
| 2025 | Great Britain   | 608           | 826             | 0.736            | ~0.74    |
| 2023 | Monaco          | 444           | 1515            | 0.293            | ~0.29    |
| 2024 | Monaco          | 0             | 1237            | 0.000            | 0.0      |
| 2025 | Monaco          | 0             | 1425            | 0.000            | 0.0      |

Non-clobbering confirmed on the real DBs: 2023 had 110 pre-existing
`session_rain_flag` rows from the heavy pipeline — after the wet populator, all
22 race sessions carry BOTH `session_rain_flag` AND `wet_lap_fraction` (0 rain
flags wiped); 2024 had no prior surface rows, so the wet populator created fresh
rows with the sibling columns left NULL.

Other notable populated wet races (season sweep): Emilia Romagna 2022 (0.291),
Singapore 2022 (0.622), Japan 2022 (1.000), Netherlands 2023 (0.244), Canada
2024 (0.665), Brazil 2024 (1.000), Australia 2025 (0.809), Belgium 2025 (0.272),
Turkey 2021 (0.999), Canada 2026 (0.012 — below threshold, stays dry).

### Validation script — wet races flagged/excluded in the PRIMARY section
```bash
py scripts/validate_burn_rate_hypothesis.py
```
**Result:** pass. Updated PRIMARY ceiling table (wetfrac column + WET flag added;
dry-baseline summary now excludes wet races):

```
  year circuit          kg/lap  laps  total kg  max kg  % of max  wetfrac     flag
  2022 Monaco            0.950    64      60.8     110       55%    0.338      WET
  2023 Monaco            0.974    78      75.9     110       69%    0.293      WET
  2024 Silverstone       1.340    52      69.7     110       63%    0.244      WET
  2025 Silverstone       1.338    52      69.6     110       63%    0.736      WET
  ...
  WET-EXCLUDED: 4 rain-affected race(s) (wet_lap_fraction >= 0.05) omitted from the dry-baseline summary below.
  SUMMARY (dry races only): n=25  mean %-of-max=85%  min=71%  max=91%  n_over_ceiling=0
  CONFIDENT: every dry-race per-race total is under the regulated ceiling ...
```
The Silverstone "anomaly" is resolved: Silverstone 2024/2025 (63% of max — clear
outliers below the ~85–91% dry cluster) are now flagged WET and dropped from the
baseline, while dry Spain (0.000) is kept. Dry summary tightened from 29→25 races.
(A pre-existing `RuntimeWarning: overflow` from the 2026 sparse-data polyfit
cross-check is unrelated to this change.)

### Simplification limits
```bash
py -m src.utils.simplification_limits --paths src/data/weather_features.py src/data/database/_ingest.py src/data/database/_core.py scripts/populate_wet_features.py src/physics/burn_rate_calibration.py scripts/validate_burn_rate_hypothesis.py
```
**Result:** pass — `PASS (6 files checked)`.

## TDD evidence, if required
- Detection tests authored first (hand-computed: all-dry→0.0; mixed→count/total;
  all-inter→1.0; case-insensitive; empty→None fraction).
- First isolated collectable run of the detection tests: green (see caveat under
  Test mode — shared test file couldn't collect a standalone red until sibling
  symbols existed; detection logic is pure and hand-verified).
- Refactor while green: yes — extracted `_ensure_session_surface_features` in
  `_core.py` to satisfy the simplification limit; all 178 tests stayed green.

## Docs/contracts touched
- None beyond in-file docstrings. The three new columns and the two new public
  functions (`session_wet_lap_features`, `populate_wet_features_for_db`,
  `session_wet_fraction`) are documented inline. No committed report-schema doc
  covers `session_surface_features`, so no external doc update was warranted.

## Assumptions
- The populator iterates every `session_type='R'` session in a season DB (via
  `DatabaseManager.get_sessions(session_type="R")`) and writes a row even when a
  race has 0 laps (`total_lap_count=0`, `wet_lap_fraction=NULL`) — honest
  missingness, not a faked zero. 2026 has several R sessions with 0 laps (future
  rounds); they store NULL fractions and are skipped by the physics consumer.
- `session_wet_fraction` reads the stored value from the season lap-times DB
  (`data/f1_data_{year}.db`), which is where the populator writes and where the
  validation script already points its `_lap_times_db_path`. It returns None on
  an un-migrated DB (missing column), a missing race row, or a NULL fraction.
- The validation script's exclude path treats a race as WET when
  `wet_lap_fraction >= WET_EXCLUDE_THRESHOLD` (0.05) and `n/a` (None) as dry
  (kept), matching "small dry race is kept".

## Stop conditions hit
- None. The ON CONFLICT upsert preserves sibling columns as specified (verified
  on synthetic and real DBs), the migration is idempotent within the existing
  pattern, and every season DB ran cleanly.

## Out-of-scope observations
- **Pre-existing simplification violation:** `_apply_schema_upgrades` in
  `src/data/database/_core.py` was ALREADY 104 lines (> the 100-line limit)
  BEFORE this change (verified by stashing my edit: it failed identically at
  104). Adding the required DDL mirror + migration pushed it to 108. To land a
  PASS within allowed scope, I extracted the whole `session_surface_features`
  create+migrate block into a cohesive module-level `_ensure_session_surface_
  features(conn)` helper, which brought the parent function back under 100. The
  function is still a long linear sequence of unrelated `CREATE TABLE`/`CREATE
  INDEX` blocks (sessions, gap_weather, surface_features, race_start_order,
  entry_list, terrain meta/samples) and is a good candidate for a broader
  table-by-table extraction refactor — flagging for triage, not done here to
  avoid scope creep into unrelated pre-existing DDL.
- **Stale `sessions.has_telemetry` flag** (already noted in the validation
  script's `_has_data` docstring) persists; not in scope here.

## Workflow Feedback
- **Handoff gaps:** The handoff was unusually complete — task, both DDL
  locations, the exact ON CONFLICT shape, the STOP-if-clobber rule, the known
  verification table, and per-file scope were all spelled out, which made this
  low-friction. One gap: the handoff did not mention that `_apply_schema_
  upgrades` was *already* over the simplification line-limit, so the
  "`simplification_limits ... must pass`" constraint (Constraints section)
  collided with close-criterion 2's "extend `_apply_schema_upgrades`" the moment
  I added the required lines. I resolved it in-scope by extracting a helper, but
  a one-line heads-up ("note: that function is near the line cap; extract if
  needed") would have saved a diagnosis loop.
- **Context rediscovered:** That `session_wet_fraction` should read from
  `data/f1_data_{year}.db` (not the telemetry store) had to be inferred from the
  existing `_lap_times_db_path` / `_green_flag_lap_times` conventions — the
  handoff's helper signature `session_wet_fraction(year, gp_name,
  lap_times_db_path)` implied it, but stating "reads the season lap-times DB, the
  same one the populator writes" would have removed the inference. Also had to
  confirm the physics module's read-only-sqlite (not DatabaseManager-import)
  house style to keep the data↔physics import boundary clean; the handoff's "no
  new import coupling" anchor pointed the right way once found.
- **Instructions improvised around:** The single-file-imports-multiple-gates
  situation meant the detection TDD "red" couldn't be observed standalone (the
  file wouldn't collect until sibling symbols existed). The skill's TDD framing
  assumes a per-step test file; I improvised by keeping detection tests authored
  first and hand-verifying the pure logic, and reported the deviation here per
  "reporting misfit is compliance". A per-gate test file split would have
  preserved a literal red, at the cost of a scattered test surface — I judged one
  cohesive `test_wet_features.py` the better artifact.
- **What would have made this easier:** Flag pre-existing lint/limit debt in
  files the handoff directs you to extend, so the "checks must pass" constraint
  doesn't silently conflict with "add code to function X".

## Return status
`complete`

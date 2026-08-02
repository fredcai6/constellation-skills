# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g2-wet-flag` (work-id `575-fuel-burn-calibration`) — per-session graded wet-race
signal in the canonical DB, consumed by the fuel-burn calibration to exclude
rain-affected races.

## Result
`APPROVE`

Survey state: `.agent-work/575-fuel-burn-calibration/g2-wet-flag-review/review.json`
(10 checks, all pass; consolidated APPROVE, 0 failing findings).

## Handoff compliance
All 8 close criteria met, independently verified:
1. **Schema in BOTH locations** — 3 columns (`wet_lap_count INTEGER`,
   `total_lap_count INTEGER`, `wet_lap_fraction REAL`) added to `schema.sql`
   and the mirrored `_core.py` CREATE (extracted into
   `_ensure_session_surface_features`).
2. **Idempotent additive migration** — see the migration check below.
3. **Non-clobbering upsert** — `ON CONFLICT(session_id) DO UPDATE` of only the
   wet columns; NOT `INSERT OR REPLACE`. See the upsert check below.
4. **DB-only detection** — `session_wet_lap_features` counts WET/INTERMEDIATE
   (case-insensitive) purely from `lap_times.compound` via `db.get_lap_times`.
5. **Populator + CLI** — `populate_wet_features_for_db` +
   `scripts/populate_wet_features.py` (default 2019–2026 sweep, idempotent,
   timestamped).
6. **Physics consumer** — `session_wet_fraction` reads the STORED value;
   `WET_EXCLUDE_THRESHOLD = 0.05` is a named module constant; `exclude_wet`
   path added to `validate_burn_rate_hypothesis.py`; `mass_model.py` untouched.
7. **Tests** — `tests/unit/data/test_wet_features.py` (13: detection,
   migration, non-clobber, populator) + 6 physics consumer tests.
8. **Verification table reproduces** — Monaco 2023 = 0.293, Silverstone 2024 =
   0.244 / 2025 = 0.736, Spain 0.0 (confirmed against the real 2023 DB and the
   validation run).

## Scope drift
None. Only the 6 allowed tracked files, 2 new files
(`scripts/populate_wet_features.py`, `tests/unit/data/test_wet_features.py`),
and the intended 8 `data/f1_data_*.db` data-writes changed.
`src/physics/mass_model.py` has **zero diff** (`git diff HEAD` empty; absent
from the changed-files list). All 7 pre-existing untracked scratch scripts
remain `??` and unmodified. No FastF1/Open-Meteo/live call added anywhere.

## Evidence verdict
All required evidence re-run FOREGROUND by me; numbers reproduce (not trusted
from the paste):
- `py -m pytest tests/unit/data/test_wet_features.py tests/unit/physics/test_burn_rate_calibration.py -q` → **72 passed**.
- `py -m pytest tests/unit/test_weather_features.py -q` → **10 passed**
  (heavy `session_rain_flag` path unaffected).
- `py scripts/validate_burn_rate_hypothesis.py` → Silverstone 2024/2025 +
  Monaco 2022/2023 flagged **WET** and excluded; **SUMMARY (dry races only):
  n=25 … n_over_ceiling=0**.
- `py -m src.utils.simplification_limits --paths <6 files>` → **PASS (6 files
  checked)**.

Test mode (test-first detection, test-after DB-plumbing/consumer) matches the
handoff. The implementer honestly reported that the shared test file could not
show a standalone detection "red" (imports sibling gate symbols); the detection
logic is pure and hand-verified — acceptable and disclosed.

## Code/doc quality
Minimal, cohesive, project-rule compliant. Migration follows the existing
`_apply_schema_upgrades` PRAGMA-guarded ALTER idiom exactly; the
`_ensure_session_surface_features` extraction is a clean way to hold the
simplification line-cap. Physics consumer uses read-only SQLite (`mode=ro`) and
does not import the data-region populator or `DatabaseManager` — the
data↔physics boundary stays DB-mediated. Docstrings match surrounding
conventions. No external doc covers `session_surface_features`, so no doc update
was warranted.

## Map impact verdict
- **Evidence supports claimed change:** Yes. Graded `wet_lap_fraction` in the
  canonical DB and the wet-exclusion behavior are both backed by reproduced
  evidence (real-DB values + validation table).
- **Constraints not violated:** Yes. Canonical-data (DB-only, no network in the
  new path) and data/physics distinctness verified independently.
- **Notes match the diff:** Yes. `struct:data`
  (`schema.sql`, `database/{_core,_ingest}.py`, `weather_features.py`) and
  `struct:physics` (`burn_rate_calibration.py` read-only consumer) match what
  the diff touched; no missing or overstated impact.
- **Decision candidates surfaced:** N/A — design was settled in the handoff;
  no authority beyond it was needed and none was silently assumed.
- **Durable context routed:** Yes. The pre-existing `_apply_schema_upgrades`
  DDL-length observation is routed as a triage candidate (below), not dropped.

## Reconciliation check
No architecture divergence requiring Commander reconcile. The change is purely
additive (new columns, new functions, a new consumer path); it does not alter
`session_rain_flag` semantics or the heavy `derive_surface_features_for_event`
pipeline (10/10 heavy-path tests green).

### Independent deep verifications (beyond re-running the paste)
- **Migration idempotency:** Built a synthetic OLD-schema
  `session_surface_features` (no wet columns) with a populated row
  (`session_rain_flag=1`, `feature_status='heavy-ok'`, `dry_laps_in_session=42`).
  First `DatabaseManager` init added all 3 wet columns and preserved every old
  value (new column NULL); the second init was an exact no-op (identical column
  set and row, no duplicate-column error).
- **Non-clobbering on real data:** On `data/f1_data_2023.db`, all **22** race
  surface rows carry BOTH `session_rain_flag` AND `wet_lap_fraction` after the
  populator (0 rain flags wiped); Monaco 2023 = `rain_flag=1, wet_frac=0.293,
  feature_status` intact.
- **No network added:** All `urllib`/`open-meteo` references in
  `weather_features.py` are pre-existing in HEAD (the heavy
  `_open_meteo_precip_mm` at line 38, above the new code at line 181+); the only
  network-pattern line the diff *adds* is a docstring stating "No
  FastF1/Open-Meteo/live call."

## Blockers
- None.

## Out-of-scope observations
- **Pre-existing (not introduced here):** `src/data/database/_core.py::_apply_schema_upgrades`
  is a long linear sequence of unrelated `CREATE TABLE`/`CREATE INDEX` blocks
  (sessions, gap_weather, surface_features, race_start_order, entry_list,
  terrain). It was already at/over the simplification line-cap before this
  change; the implementer extracted `_ensure_session_surface_features` to land a
  PASS. A broader table-by-table extraction refactor is a good future-work
  candidate. Flagged as triage `tc1`; out of scope for g2.
- **Pre-existing:** `sessions.has_telemetry` staleness (already noted in the
  validation script's `_has_data` docstring) persists; not in scope here.
- A pre-existing `RuntimeWarning: overflow` from the 2026 sparse-data polyfit
  cross-check in the validation script is unrelated to this change.

## Workflow Feedback
- **Handoff gaps:** None material. The reviewer handoff was exceptionally
  complete — it named the exact deep checks (synthetic old-schema migration,
  real-2023-row dual-column, no-network grep, `mass_model.py` zero-diff), which
  made independent verification direct. One minor note carried over from the
  implementer: the handoff did not flag that `_apply_schema_upgrades` was
  *already* over the simplification line-cap, so a naive "extend that function"
  reading would collide with the "simplification must pass" constraint; the
  implementer resolved it in-scope and I confirmed the resolution is clean.
- **Context rediscovered:** Only the `DatabaseManager` import path
  (`src.data.database` package re-export, backed by `.manager`, not a
  `.database` submodule) — trivial, discovered in one probe. The handoff's
  close-criterion 2 says "re-run the migration twice against a synthetic
  old-schema DB": the migration is reached via `DatabaseManager(db_path=...)`
  init (which calls `_apply_schema_upgrades`), not a standalone entrypoint — a
  one-line "invoke via DatabaseManager init" would have saved the probe.
- **Instructions improvised around:** None. The survey template's inherited-rule
  guidance (append one check per inherited rule) fit cleanly — I appended r6–r9
  for the four handoff-named deep checks and the engine drove them to
  consolidation without friction.
- **What would have made this easier:** Nothing substantive. Optionally, state
  in the handoff that the migration entrypoint is `DatabaseManager.__init__`
  (not a named public migration function), so the "re-run twice" instruction is
  unambiguous about *how* to invoke it.

## Return status
`complete`

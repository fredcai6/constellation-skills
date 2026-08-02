# Reviewer Handoff — per-session wet-race flag (data region)

## Gate
`g2-wet-flag` (work-id `575-fuel-burn-calibration`)

## Survey State Location
`.agent-work/575-fuel-burn-calibration/g2-wet-flag-review/review.json`

## What Was Implemented
Extended the per-session `session_surface_features` table with three new
columns (`wet_lap_count`, `total_lap_count`, `wet_lap_fraction`), an idempotent
additive migration, a non-clobbering `ON CONFLICT DO UPDATE` upsert that owns
only the new columns, a DB-only detection function (WET/INTERMEDIATE compound
fraction) in `weather_features.py`, an all-seasons populator + CLI
(`scripts/populate_wet_features.py`, run over 2019-2026), and a physics
consumer helper (`session_wet_fraction`) + a wet-exclusion path in
`scripts/validate_burn_rate_hypothesis.py`. Purpose: exclude rain-affected
races (Silverstone 2024/2025, Monaco 2022/2023) from the dry fuel-burn
baseline. `mass_model.py` untouched.

## How to Inspect the Diff
```
git status --porcelain
git diff HEAD -- src/data/schema.sql src/data/database/_core.py src/data/database/_ingest.py src/data/weather_features.py src/physics/burn_rate_calibration.py scripts/validate_burn_rate_hypothesis.py
```
New files: `scripts/populate_wet_features.py`, `tests/unit/data/test_wet_features.py`.
Branch `feat/575-fuel-burn-calibration`. NOTE: the 8 `data/f1_data_*.db` files
show as modified (the populator wrote the wet columns) — that is expected data
population, not a code concern; do not flag their presence, but DO confirm
`mass_model.py` has zero diff and no pre-existing untracked scratch script was
modified. Full implementer result:
`.agent-work/575-fuel-burn-calibration/crew-handoffs/g2-wet-flag-implementer-result.md`.

## Task Statement
See the implementer handoff
`.agent-work/575-fuel-burn-calibration/crew-handoffs/g2-wet-flag-implementer-handoff.md`
for the full settled design and close criteria.

## Close Criteria (verify each)
1. Schema columns added in BOTH `schema.sql` AND `_core.py`'s mirrored CREATE.
2. Migration is idempotent and additive: on an OLD-schema
   `session_surface_features` (no new columns), `_apply_schema_upgrades` adds
   them; running twice is a no-op; existing rows keep their old values.
   Re-run the migration twice against a synthetic old-schema DB yourself.
3. The wet upsert is genuinely NON-CLOBBERING: writing wet columns must leave a
   pre-existing `session_rain_flag`/`feature_status`/`dry_laps_*` on the same
   row intact (verify by reading the code AND by the test, and ideally by
   querying a real 2023 DB row that has both a heavy-pipeline
   `session_rain_flag` and the new `wet_lap_fraction`). Confirm it does NOT use
   `INSERT OR REPLACE`.
4. Detection is DB-only (no FastF1/Open-Meteo import in the new code path):
   `grep -rn "fastf1\|open_meteo\|requests\|urllib" src/data/weather_features.py scripts/populate_wet_features.py` — the new code must not add a network call.
5. Physics consumer reads the STORED value (does not recompute compounds inside
   physics); `WET_EXCLUDE_THRESHOLD` is a named constant (0.05), not a magic
   literal.
6. Re-run the verification commands yourself and confirm they pass and the
   numbers reproduce (do NOT trust the pasted output):
   - `py -m pytest tests/unit/data/test_wet_features.py tests/unit/physics/test_burn_rate_calibration.py -q`
   - `py -m pytest tests/unit/test_weather_features.py -q` (heavy path unaffected)
   - `py scripts/validate_burn_rate_hypothesis.py` — confirm Silverstone
     2024/2025 + Monaco 2022/2023 are flagged WET and excluded, dry summary
     n=25.
   - `py -m src.utils.simplification_limits --paths <the 6 touched files>`

## Allowed Scope / Exclusions
As per the implementer handoff. Flag it as a finding if `mass_model.py` was
touched, a scratch script was modified, a network call was added, or the upsert
clobbers sibling columns.

## Constraints the Implementation Must Respect
- Additive migration only, following the existing `_apply_schema_upgrades`
  idiom.
- DB-only / canonical-data constraint.
- `session_rain_flag` semantics and the heavy `derive_surface_features_for_event`
  path unchanged (the 10 `test_weather_features.py` tests must still pass).
- Data/physics regions stay distinct — physics reads the stored flag via the
  DB, no import of the data-region populator into physics.

## Map Anchors (inbound)
Inherits the g2-wet-flag implementer anchors: `struct:data`
(`schema.sql`, `database/{_core,_ingest}.py`, `weather_features.py`),
`struct:physics` (`burn_rate_calibration.py` read-only consumer);
canonical-data constraint; data/physics distinctness.

## Evidence Produced
See the implementer result's Evidence section (72+178 tests pass, populator
over 2019-2026 reproduces the known wet-fraction table, validation excludes 4
wet races, simplification PASS). Re-derive, don't trust.

## Suggested Model Tier
Stronger — a data-region schema/migration change with a non-clobbering-upsert
correctness subtlety and a cross-region consumer.

## Stop Conditions
Return BLOCK if: any verification command fails on re-run, the migration is not
idempotent, the upsert clobbers sibling columns, a network call was added, or
`mass_model.py`/scratch scripts were touched.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers,
out-of-scope observations, workflow feedback.

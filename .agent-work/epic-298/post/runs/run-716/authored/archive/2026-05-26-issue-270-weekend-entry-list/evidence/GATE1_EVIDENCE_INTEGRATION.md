# Evidence Integration: Gate 1

## Implementer Evidence

Status: complete

Changed files:
- `src/data/schema.sql`
- `src/data/database.py`
- `src/data/collector.py`
- `src/evo_predictor/data_adapter.py`
- `tests/unit/test_collector.py`
- `tests/unit/evo_predictor/test_data_adapter.py`

Behavior implemented:
- Added durable `weekend_entry_list` schema plus additive migration.
- Added strict `DatabaseManager.upsert_weekend_entry_list(...)` and `get_weekend_entry_list(...)`.
- Collector stores available `session.drivers`, normalized through `session.results` to DB driver abbreviations when possible.
- `build_all_race_features` uses DB entry-list eligibility when present, otherwise keeps current actual-derived fallback.
- Added DB, collector, and evo training behavior tests.

Implementer evidence:
- Red first: focused command failed on missing DB methods / missing collector and adapter wiring.
- `py -m pytest tests/unit/test_collector.py tests/unit/evo_predictor/test_data_adapter.py -v` -> `85 passed`
- `py -m pytest tests/unit/evo_predictor -v` -> `949 passed, 69 warnings`
- `py -m pytest tests/unit/ -v` -> `2279 passed, 10 skipped, 73 warnings`

## Pilot Inspection

Status: complete

Checks:
- schema migration is additive
- DB methods fail clearly on invalid inputs; added non-string driver-id rejection
- collector persists only fully mapped abbreviation driver IDs
- collector preserves an existing event entry list instead of redefining it from later sessions
- evo training uses DB entry list only through `DatabaseManager`
- fallback is explicit and tested

Pilot fix evidence after first review block:
- `py -m pytest tests/unit/test_collector.py tests/unit/evo_predictor/test_data_adapter.py -v` -> `89 passed`
- `py -m pytest tests/unit/evo_predictor -v` -> `949 passed, 69 warnings`
- `py -m pytest tests/unit/ -v` -> `2283 passed, 10 skipped, 73 warnings`

## Reviewer Evidence

Status: complete

First reviewer result: BLOCK.
- P1: collector replaced the whole event entry list from every collected session, making the canonical list collection-order dependent.
- P1: `_extract_session_drivers` could persist raw FastF1 driver numbers when mapping metadata was absent.

Second reviewer result after fixes: APPROVE.
- Previous overwrite blocker resolved by `_store_weekend_entry_list_if_absent`.
- Previous raw-number blocker resolved by requiring complete `DriverNumber` -> `Abbreviation` mapping.
- Residual risks: no full collector-to-training integration test; telemetry collection path shares helper but is not directly tested; first successful session still defines the list when none exists.

## Gate Decision

Status: closed

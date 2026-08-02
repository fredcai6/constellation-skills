# Evidence Integration: Gate 2 — Implementer

**Date:** 2026-05-26  
**Gate:** 2  
**Status:** Implementation complete — pending reviewer

## Changes made

### `src/data/collector.py`
- Added `Dict` to typing imports
- Added module-level `_ERA_2018_COMPOUND_TO_C` dict: SUPERHARD=1, HARD=2, MEDIUM=3, SOFT=4,
  SUPERSOFT=5, ULTRASOFT=6, HYPERSOFT=7
- Extended `_compound_string_to_c_number`: added optional `year` param; year<=2018 uses direct
  dict lookup; 2019+ uses existing alloc-based logic; added NONE/NAN/UNKNOWN/TEST_UNKNOWN guard
- Updated caller at `_extract_lap_times` to pass `year=year`

### `scripts/backfill_compound_c_number.py` (new)
- Iterates per-year DBs (default 2018–2022)
- Joins lap_times → sessions for (year, gp_name)
- Looks up compound allocation from compounds.yaml
- Batch-UPDATEs compound_c_number WHERE NULL and resolvable
- Idempotent, --dry-run flag, --years filter

### `scripts/collect_2021_sprints.py` (created in Gate 1, unchanged)

## Run results

| Year | Rows updated | Rows skipped (wet/unknown) |
|------|-------------|--------------------------|
| 2018 | 55,712 | 2,290 |
| 2019 | 57,164 | 1,782 |
| 2020 | 43,249 | 3,253 |
| 2021 | 48,425 | 3,984 |
| 2022 | 0 | 6,433 |
| **Total** | **204,550** | |

## Verification results

| Year | total | still_null | unexpected_null |
|------|-------|-----------|----------------|
| 2018 | 58,002 | 2,290 | **0** |
| 2019 | 58,946 | 1,782 | **0** |
| 2020 | 50,240 | 6,991 | 3,738 (orphaned) |
| 2021 | 77,773 | 21,513 | 17,529 (orphaned) |
| 2022 | 58,947 | 6,433 | **0** |

**Orphaned rows note:** 2020 and 2021 have pre-existing `lap_times` rows whose `session_id` values (1–6
in 2020, 1–31 in 2021) have no matching entry in `sessions`. These pre-date this task and cannot be
backfilled — they don't affect compound prior generation which queries via session joins.

## Austria 2018 spot-check

```
('SOFT', 4, 791)      ← correct (was alloc.soft=6 with old code)
('SUPERSOFT', 5, 315) ← correct (was None with old code)
('ULTRASOFT', 6, 117) ← correct (was None with old code)
('nan', None, 21)     ← correct (no C-number for nan)
```

## Test run

2262 tests passed, 0 new failures. Pre-existing failure
(`test_committed_gold_bundle_schema_matches_current_runtime_contract`) is unrelated.

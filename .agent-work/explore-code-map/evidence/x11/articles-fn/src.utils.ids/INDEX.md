[map index](../INDEX.md)

# `src.utils.ids`

> Driver ID Mapping Utility
>
> This module handles mapping between FastF1 and Ergast driver identifiers,
> including manual overrides for edge cases and name mismatches.

*(everything after the first line above is [s].)*

`src/utils/ids.py` · 325 lines [s] · 10 entities · 10 documented, 0 **holes**

## Dependencies

**Imports (stdlib)**: `logging`, `typing.Dict`, `typing.List`, `typing.Optional`
**Imports (third-party)**: `pandas`, `yaml`

**Imported by**: no importer inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted, so this is *not* evidence the module is unused).

## Module-level constants

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `logger` | — | `logging.getLogger(__name__)` | 14 | name only |

## Contents

- [`DriverMapper`](DriverMapper.md) — *class* [s] — Maps driver identifiers between FastF1 and Ergast systems
  - [`DriverMapper.__init__`](DriverMapper.__init__.md) — *method* [s] — Initialize driver mapper
  - [`DriverMapper._load_manual_mappings`](DriverMapper._load_manual_mappings.md) — *method* [s] — Load manual override mappings from YAML file
  - [`DriverMapper.map_driver_code`](DriverMapper.map_driver_code.md) — *method* [s] — Map driver code between systems
  - [`DriverMapper.map_driver_name`](DriverMapper.map_driver_name.md) — *method* [s] — Map driver name to standard format
  - [`DriverMapper.create_mapping_table`](DriverMapper.create_mapping_table.md) — *method* [s] — Create a comprehensive mapping table between FastF1 and Ergast drivers
  - [`DriverMapper.get_driver_consistency_score`](DriverMapper.get_driver_consistency_score.md) — *method* [s] — Calculate consistency score between FastF1 and Ergast driver data
  - [`DriverMapper.suggest_mappings`](DriverMapper.suggest_mappings.md) — *method* [s] — Suggest potential driver mappings based on name similarity
  - [`DriverMapper.export_mappings`](DriverMapper.export_mappings.md) — *method* [s] — Export driver mappings to a file
  - [`DriverMapper.validate_mapping`](DriverMapper.validate_mapping.md) — *method* [s] — Validate if a driver mapping is correct
---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

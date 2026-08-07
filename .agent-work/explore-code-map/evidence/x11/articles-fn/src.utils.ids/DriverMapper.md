[map index](../INDEX.md) / [`src.utils.ids`](INDEX.md)

# `DriverMapper`
*class* [s] · [`src/utils/ids.py:16`](C:/Programs/f1Brainz/src/utils/ids.py#L16) · 310 lines [s]

```python
class DriverMapper
```

> Maps driver identifiers between FastF1 and Ergast systems
>
> Handles:
> - FastF1 DriverNumber/Abbreviation ↔ Ergast driverId/code
> - Manual override mappings for edge cases
> - Driver aliases and name variations

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Members**

- [`DriverMapper.__init__`](DriverMapper.__init__.md) — *method* — Initialize driver mapper
- [`DriverMapper._load_manual_mappings`](DriverMapper._load_manual_mappings.md) — *method* — Load manual override mappings from YAML file
- [`DriverMapper.map_driver_code`](DriverMapper.map_driver_code.md) — *method* — Map driver code between systems
- [`DriverMapper.map_driver_name`](DriverMapper.map_driver_name.md) — *method* — Map driver name to standard format
- [`DriverMapper.create_mapping_table`](DriverMapper.create_mapping_table.md) — *method* — Create a comprehensive mapping table between FastF1 and Ergast drivers
- [`DriverMapper.get_driver_consistency_score`](DriverMapper.get_driver_consistency_score.md) — *method* — Calculate consistency score between FastF1 and Ergast driver data
- [`DriverMapper.suggest_mappings`](DriverMapper.suggest_mappings.md) — *method* — Suggest potential driver mappings based on name similarity
- [`DriverMapper.export_mappings`](DriverMapper.export_mappings.md) — *method* — Export driver mappings to a file
- [`DriverMapper.validate_mapping`](DriverMapper.validate_mapping.md) — *method* — Validate if a driver mapping is correct

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | stdlib | `builtins.str` x17, `typing.Dict` x4, `typing.Optional` x3, `builtins.bool`, `builtins.float`, `typing.List` |
| reads | third-party | `pandas (module)` x9, `pandas.DataFrame` x9 |

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

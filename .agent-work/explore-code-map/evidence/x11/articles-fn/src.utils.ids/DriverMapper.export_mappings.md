[map index](../INDEX.md) / [`src.utils.ids`](INDEX.md) / [`DriverMapper`](DriverMapper.md)

# `DriverMapper.export_mappings`
*method* [s] · [`src/utils/ids.py:274`](C:/Programs/f1Brainz/src/utils/ids.py#L274) · 28 lines [s]

**Signature** [s]

```python
def export_mappings(self, output_file: str, fastf1_data: pd.DataFrame, ergast_data: pd.DataFrame)
```

> Export driver mappings to a file
>
> Args:
>     output_file: Output file path
>     fastf1_data: FastF1 driver data
>     ergast_data: Ergast driver data

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `output_file` — output_file: Output file path [a]
- `fastf1_data` — fastf1_data: FastF1 driver data [a]
- `ergast_data` — ergast_data: Ergast driver data [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `DriverMapper.create_mapping_table`, `DriverMapper.suggest_mappings` |
| calls | third-party | `pandas.DataFrame` |
| reads | internal | `logger` x3 |
| reads | stdlib | `builtins.Exception` |
| reads | third-party | `pandas (module)` |

*Not shown: 7 local-variable reads, 4 local-variable writes; 9 reads of its own parameters.*

**Unresolved by the extractor**: 6 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

[map index](../INDEX.md) / [`src.utils.ids`](INDEX.md) / [`DriverMapper`](DriverMapper.md)

# `DriverMapper.get_driver_consistency_score`
*method* [s] · [`src/utils/ids.py:189`](C:/Programs/f1Brainz/src/utils/ids.py#L189) · 33 lines [s]

**Signature** [s]

```python
def get_driver_consistency_score(self, fastf1_data: pd.DataFrame, ergast_data: pd.DataFrame) -> Dict[str, float]
```

> Calculate consistency score between FastF1 and Ergast driver data
>
> Args:
>     fastf1_data: FastF1 driver data
>     ergast_data: Ergast driver data
>
> Returns:
>     Dictionary with consistency metrics

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `fastf1_data` — fastf1_data: FastF1 driver data [a]
- `ergast_data` — ergast_data: Ergast driver data [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `DriverMapper.create_mapping_table` |
| calls | stdlib | `builtins.len` x2 |
| reads | internal | `logger` |
| reads | stdlib | `builtins.Exception` |

*Not shown: 13 local-variable reads, 4 local-variable writes; 3 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

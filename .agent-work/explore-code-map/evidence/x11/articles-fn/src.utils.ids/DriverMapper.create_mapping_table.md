[map index](../INDEX.md) / [`src.utils.ids`](INDEX.md) / [`DriverMapper`](DriverMapper.md)

# `DriverMapper.create_mapping_table`
*method* [s] · [`src/utils/ids.py:129`](C:/Programs/f1Brainz/src/utils/ids.py#L129) · 59 lines [s]

**Signature** [s]

```python
def create_mapping_table(self, fastf1_drivers: pd.DataFrame, ergast_drivers: pd.DataFrame) -> pd.DataFrame
```

> Create a comprehensive mapping table between FastF1 and Ergast drivers
>
> Args:
>     fastf1_drivers: DataFrame with FastF1 driver data
>     ergast_drivers: DataFrame with Ergast driver data
>
> Returns:
>     DataFrame with driver mappings

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `fastf1_drivers` — fastf1_drivers: DataFrame with FastF1 driver data [a]
- `ergast_drivers` — ergast_drivers: DataFrame with Ergast driver data [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.len` |
| calls | third-party | `pandas.DataFrame` x2 |
| reads | internal | `logger` x2 |
| reads | stdlib | `builtins.Exception` |
| reads | third-party | `pandas (module)` x2 |

*Not shown: 21 local-variable reads, 11 local-variable writes; 4 reads of its own parameters.*

**Unresolved by the extractor**: 11 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

**Referenced by**: 3 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

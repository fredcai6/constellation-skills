[map index](../INDEX.md) / [`src.utils.ids`](INDEX.md) / [`DriverMapper`](DriverMapper.md)

# `DriverMapper.suggest_mappings`
*method* [s] · [`src/utils/ids.py:223`](C:/Programs/f1Brainz/src/utils/ids.py#L223) · 50 lines [s]

**Signature** [s]

```python
def suggest_mappings(self, fastf1_data: pd.DataFrame, ergast_data: pd.DataFrame) -> List[Dict[str, str]]
```

> Suggest potential driver mappings based on name similarity
>
> Args:
>     fastf1_data: FastF1 driver data
>     ergast_data: Ergast driver data
>
> Returns:
>     List of suggested mappings

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `fastf1_data` — fastf1_data: FastF1 driver data [a]
- `ergast_data` — ergast_data: Ergast driver data [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `DriverMapper.create_mapping_table` |
| calls | stdlib | `builtins.len` |
| reads | internal | `logger` x2 |
| reads | stdlib | `builtins.Exception` |

*Not shown: 21 local-variable reads, 11 local-variable writes; 4 reads of its own parameters.*

**Unresolved by the extractor**: 14 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

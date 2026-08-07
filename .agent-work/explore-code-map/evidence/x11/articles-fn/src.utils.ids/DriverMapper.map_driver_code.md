[map index](../INDEX.md) / [`src.utils.ids`](INDEX.md) / [`DriverMapper`](DriverMapper.md)

# `DriverMapper.map_driver_code`
*method* [s] · [`src/utils/ids.py:77`](C:/Programs/f1Brainz/src/utils/ids.py#L77) · 25 lines [s]

**Signature** [s]

```python
def map_driver_code(self, driver_code: str, source: str = 'fastf1') -> Optional[str]
```

> Map driver code between systems
>
> Args:
>     driver_code: Driver code to map
>     source: Source system ('fastf1' or 'ergast')
>
> Returns:
>     Mapped driver code or None if no mapping found

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `driver_code` — driver_code: Driver code to map [a]
- `source` — source: Source system ('fastf1' or 'ergast') [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `DriverMapper.manual_mappings` x3, `DriverMapper.driver_aliases` x2 |

*Not shown: 14 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

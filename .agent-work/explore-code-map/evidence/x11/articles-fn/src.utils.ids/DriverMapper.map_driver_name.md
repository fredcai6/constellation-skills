[map index](../INDEX.md) / [`src.utils.ids`](INDEX.md) / [`DriverMapper`](DriverMapper.md)

# `DriverMapper.map_driver_name`
*method* [s] · [`src/utils/ids.py:103`](C:/Programs/f1Brainz/src/utils/ids.py#L103) · 25 lines [s]

**Signature** [s]

```python
def map_driver_name(self, first_name: str, last_name: str, source: str = 'fastf1') -> Optional[str]
```

> Map driver name to standard format
>
> Args:
>     first_name: Driver's first name
>     last_name: Driver's last name
>     source: Source system
>
> Returns:
>     Standardized driver name or None if no mapping found

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `first_name` — first_name: Driver's first name [a]
- `last_name` — last_name: Driver's last name [a]
- `source` — source: Source system [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `DriverMapper.driver_aliases` |

*Not shown: 4 local-variable reads, 3 local-variable writes; 5 reads of its own parameters.*

**Unresolved by the extractor**: 3 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

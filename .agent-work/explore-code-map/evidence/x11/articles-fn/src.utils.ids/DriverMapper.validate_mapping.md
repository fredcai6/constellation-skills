[map index](../INDEX.md) / [`src.utils.ids`](INDEX.md) / [`DriverMapper`](DriverMapper.md)

# `DriverMapper.validate_mapping`
*method* [s] · [`src/utils/ids.py:303`](C:/Programs/f1Brainz/src/utils/ids.py#L303) · 23 lines [s]

**Signature** [s]

```python
def validate_mapping(self, fastf1_code: str, ergast_code: str) -> bool
```

> Validate if a driver mapping is correct
>
> Args:
>     fastf1_code: FastF1 driver code
>     ergast_code: Ergast driver code
>
> Returns:
>     True if mapping is valid, False otherwise

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `fastf1_code` — fastf1_code: FastF1 driver code [a]
- `ergast_code` — ergast_code: Ergast driver code [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `DriverMapper.manual_mappings` x3, `DriverMapper.driver_aliases` x2 |

*Not shown: 13 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

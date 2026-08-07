[map index](../INDEX.md) / [`src.utils.f1_calendar`](INDEX.md)

# `get_race_by_name`
*function* [s] · [`src/utils/f1_calendar.py:383`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L383) · 3 lines [s]

**Signature** [s]

```python
def get_race_by_name(season: int, gp_name: str) -> Optional[RaceInfo]
```

> Get race by name. See F1Calendar.get_race_by_name.

**Parameters**

- `season` — *[HOLE] undocumented parameter*
- `gp_name` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `get_calendar` |

*Not shown: 2 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

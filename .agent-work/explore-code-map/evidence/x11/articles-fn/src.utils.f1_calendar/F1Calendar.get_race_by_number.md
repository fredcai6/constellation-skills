[map index](../INDEX.md) / [`src.utils.f1_calendar`](INDEX.md) / [`F1Calendar`](F1Calendar.md)

# `F1Calendar.get_race_by_number`
*method* [s] · [`src/utils/f1_calendar.py:159`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L159) · 16 lines [s]

**Signature** [s]

```python
def get_race_by_number(self, season: int, race_number: int) -> Optional[RaceInfo]
```

> Get race info by race number.
>
> Args:
>     season: Season year
>     race_number: Race number (1-indexed)
>
> Returns:
>     RaceInfo if found, None otherwise

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — season: Season year [a]
- `race_number` — race_number: Race number (1-indexed) [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar.get_season_calendar` |

*Not shown: 3 local-variable reads, 2 local-variable writes; 3 reads of its own parameters.*

**Unresolved by the extractor**: 1 reads (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

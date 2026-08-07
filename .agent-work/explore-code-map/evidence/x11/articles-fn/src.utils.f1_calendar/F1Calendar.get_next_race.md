[map index](../INDEX.md) / [`src.utils.f1_calendar`](INDEX.md) / [`F1Calendar`](F1Calendar.md)

# `F1Calendar.get_next_race`
*method* [s] · [`src/utils/f1_calendar.py:242`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L242) · 17 lines [s]

**Signature** [s]

```python
def get_next_race(self, season: int, reference_date: Optional[datetime] = None) -> Optional[RaceInfo]
```

> Get the next race after reference date.
>
> Args:
>     season: Season year
>     reference_date: Reference date (default: now)
>
> Returns:
>     Next RaceInfo or None if season is over

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — season: Season year [a]
- `reference_date` — reference_date: Reference date (default: now) [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar.get_upcoming_races` |

*Not shown: 2 local-variable reads, 1 local-variable writes; 3 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

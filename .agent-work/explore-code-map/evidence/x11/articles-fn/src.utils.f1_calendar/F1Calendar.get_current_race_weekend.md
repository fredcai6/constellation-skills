[map index](../INDEX.md) / [`src.utils.f1_calendar`](INDEX.md) / [`F1Calendar`](F1Calendar.md)

# `F1Calendar.get_current_race_weekend`
*method* [s] · [`src/utils/f1_calendar.py:295`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L295) · 33 lines [s]

**Signature** [s]

```python
def get_current_race_weekend(self, season: int, check_date: Optional[datetime] = None) -> Optional[RaceInfo]
```

> Get race info if currently on a race weekend.
>
> Args:
>     season: Season year
>     check_date: Date to check (default: now)
>
> Returns:
>     RaceInfo if on race weekend, None otherwise

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — season: Season year [a]
- `check_date` — check_date: Date to check (default: now) [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar._naive_datetime` x2, `F1Calendar.get_season_calendar` |
| calls | stdlib | `datetime.datetime.now` |
| reads | stdlib | `datetime.datetime` x2, `datetime.datetime.min` |
| writes | internal | `F1Calendar.get_current_race_weekend.check_date` |

*Not shown: 5 local-variable reads, 3 local-variable writes; 6 reads of its own parameters.*

**Unresolved by the extractor**: 3 reads (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

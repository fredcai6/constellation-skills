[map index](../INDEX.md) / [`src.utils.f1_calendar`](INDEX.md) / [`F1Calendar`](F1Calendar.md)

# `F1Calendar.get_upcoming_races`
*method* [s] · [`src/utils/f1_calendar.py:200`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L200) · 41 lines [s]

**Signature** [s]

```python
def get_upcoming_races(self, season: int, days_ahead: int = 7, reference_date: Optional[datetime] = None) -> List[RaceInfo]
```

> Get upcoming races within specified days.
>
> Args:
>     season: Season year
>     days_ahead: Number of days to look ahead
>     reference_date: Reference date (default: now)
>
> Returns:
>     List of RaceInfo for upcoming races

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — season: Season year [a]
- `days_ahead` — days_ahead: Number of days to look ahead [a]
- `reference_date` — reference_date: Reference date (default: now) [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar.get_season_calendar` |
| calls | stdlib | `builtins.hasattr` x2, `builtins.sorted`, `datetime.datetime.now` |
| reads | stdlib | `datetime.datetime` x2, `datetime.datetime.min` |
| writes | internal | `F1Calendar.get_upcoming_races.reference_date` |

*Not shown: 15 local-variable reads, 8 local-variable writes; 5 reads of its own parameters.*

**Unresolved by the extractor**: 3 calls (dispatch-unknown-base), 6 reads (dispatch-unknown-base), 1 reads (unbound-name)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

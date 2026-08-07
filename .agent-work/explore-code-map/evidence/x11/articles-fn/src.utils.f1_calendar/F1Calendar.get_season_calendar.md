[map index](../INDEX.md) / [`src.utils.f1_calendar`](INDEX.md) / [`F1Calendar`](F1Calendar.md)

# `F1Calendar.get_season_calendar`
*method* [s] · [`src/utils/f1_calendar.py:54`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L54) · 75 lines [s]

**Signature** [s]

```python
def get_season_calendar(self, season: int, force_refresh: bool = False) -> List[RaceInfo]
```

> Get full calendar for a season.
>
> Args:
>     season: Season year
>     force_refresh: Force reload even if cached
>
> Returns:
>     List of RaceInfo for all races in season

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — season: Season year [a]
- `force_refresh` — force_refresh: Force reload even if cached [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar._get_fallback_calendar`, `RaceInfo` |
| calls | cross-module | `src.utils.constants:SPRINT_WEEKENDS.get` |
| calls | stdlib | `builtins.int`, `builtins.len` |
| calls | third-party | `fastf1.get_event_schedule` |
| reads | internal | `F1Calendar._cache` x3, `logger` x2 |
| reads | cross-module | `src.utils.constants:SPRINT_WEEKENDS` |
| reads | stdlib | `builtins.Exception` |
| reads | third-party | `fastf1 (module)` |
| writes | internal | `F1Calendar._cache[]` |

*Not shown: 37 local-variable reads, 17 local-variable writes; 14 reads of its own parameters.*

**Unresolved by the extractor**: 15 calls (dispatch-unknown-base)

**Referenced by**: 5 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

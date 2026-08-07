[map index](../INDEX.md) / [`src.utils.f1_calendar`](INDEX.md) / [`F1Calendar`](F1Calendar.md)

# `F1Calendar._get_fallback_calendar`
*method* [s] · [`src/utils/f1_calendar.py:130`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L130) · 28 lines [s]

**Signature** [s]

```python
def _get_fallback_calendar(self, season: int) -> List[RaceInfo]
```

> Fallback calendar when FastF1 unavailable.
>
> Returns race info without dates.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `RaceInfo` |
| calls | cross-module | `src.utils.constants:F1_CALENDARS.get`, `src.utils.constants:SPRINT_WEEKENDS.get` |
| calls | stdlib | `builtins.enumerate` |
| reads | internal | `logger` |
| reads | cross-module | `src.utils.constants:F1_CALENDARS`, `src.utils.constants:SPRINT_WEEKENDS` |
| reads | stdlib | `datetime.datetime.min`, `datetime.datetime` |

*Not shown: 8 local-variable reads, 6 local-variable writes; 4 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

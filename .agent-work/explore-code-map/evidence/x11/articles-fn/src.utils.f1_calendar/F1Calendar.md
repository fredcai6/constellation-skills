[map index](../INDEX.md) / [`src.utils.f1_calendar`](INDEX.md)

# `F1Calendar`
*class* [s] · [`src/utils/f1_calendar.py:36`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L36) · 317 lines [s]

```python
class F1Calendar
```

> F1 calendar manager for race scheduling.
>
> Uses FastF1 to get actual race dates and session times.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Members**

- [`F1Calendar.__init__`](F1Calendar.__init__.md) — *method* — Initialize calendar manager.
- [`F1Calendar._naive_datetime`](F1Calendar._naive_datetime.md) — *static method* — Normalize timezone-aware datetimes for safe calendar comparison.
- [`F1Calendar.get_season_calendar`](F1Calendar.get_season_calendar.md) — *method* — Get full calendar for a season.
- [`F1Calendar._get_fallback_calendar`](F1Calendar._get_fallback_calendar.md) — *method* — Fallback calendar when FastF1 unavailable.
- [`F1Calendar.get_race_by_number`](F1Calendar.get_race_by_number.md) — *method* — Get race info by race number.
- [`F1Calendar.get_race_by_name`](F1Calendar.get_race_by_name.md) — *method* — Get race info by GP name.
- [`F1Calendar.get_upcoming_races`](F1Calendar.get_upcoming_races.md) — *method* — Get upcoming races within specified days.
- [`F1Calendar.get_next_race`](F1Calendar.get_next_race.md) — *method* — Get the next race after reference date.
- [`F1Calendar.is_race_weekend`](F1Calendar.is_race_weekend.md) — *method* — Check if date falls on a race weekend.
- [`F1Calendar.get_current_race_weekend`](F1Calendar.get_current_race_weekend.md) — *method* — Get race info if currently on a race weekend.
- [`F1Calendar.format_race_info`](F1Calendar.format_race_info.md) — *method* — Format race info for display.

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `RaceInfo` x8 |
| reads | stdlib | `builtins.int` x10, `typing.Optional` x8, `datetime.datetime` x6, `typing.List` x3, `builtins.bool` x2, `builtins.str` x2, `builtins.staticmethod` |

**Referenced by**: 2 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*

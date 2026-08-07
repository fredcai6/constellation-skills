# src.utils.f1_calendar:F1Calendar
class, src/utils/f1_calendar.py:36, 317 lines

```python
class F1Calendar
```

F1 calendar manager for race scheduling.

Uses FastF1 to get actual race dates and session times.

- [__init__](F1Calendar.__init__.md) method: Initialize calendar manager.
- [_naive_datetime](F1Calendar._naive_datetime.md) static method: Normalize timezone-aware datetimes for safe calendar comparison.
- [get_season_calendar](F1Calendar.get_season_calendar.md) method: Get full calendar for a season.
- [_get_fallback_calendar](F1Calendar._get_fallback_calendar.md) method: Fallback calendar when FastF1 unavailable.
- [get_race_by_number](F1Calendar.get_race_by_number.md) method: Get race info by race number.
- [get_race_by_name](F1Calendar.get_race_by_name.md) method: Get race info by GP name.
- [get_upcoming_races](F1Calendar.get_upcoming_races.md) method: Get upcoming races within specified days.
- [get_next_race](F1Calendar.get_next_race.md) method: Get the next race after reference date.
- [is_race_weekend](F1Calendar.is_race_weekend.md) method: Check if date falls on a race weekend.
- [get_current_race_weekend](F1Calendar.get_current_race_weekend.md) method: Get race info if currently on a race weekend.
- [format_race_info](F1Calendar.format_race_info.md) method: Format race info for display.

reads internal: RaceInfo x8
reads stdlib: builtins.int x10, typing.Optional x8, datetime.datetime x6, typing.List x3, builtins.bool x2, builtins.str x2, builtins.staticmethod

referenced by: 2 sites, this module only

# src.utils.f1_calendar
src/utils/f1_calendar.py, 390 lines

F1 calendar integration for race scheduling.

Provides utilities for tracking upcoming races, race weekends, and scheduling
automated predictions.

imports stdlib: dataclasses.dataclass, datetime.datetime, logging, typing.Dict, typing.List, typing.Optional
imports third-party: fastf1
imports internal: src.utils.constants:F1_CALENDARS, src.utils.constants:SPRINT_WEEKENDS
imported by: none found (scripts/ and tests/ not indexed)

```python
logger = logging.getLogger(__name__)
_calendar = None
```

- [RaceInfo](RaceInfo.md) class: Information about an F1 race weekend.
- [F1Calendar](F1Calendar.md) class: F1 calendar manager for race scheduling.
  - [F1Calendar.__init__](F1Calendar.__init__.md) method: Initialize calendar manager.
  - [F1Calendar._naive_datetime](F1Calendar._naive_datetime.md) static method: Normalize timezone-aware datetimes for safe calendar comparison.
  - [F1Calendar.get_season_calendar](F1Calendar.get_season_calendar.md) method: Get full calendar for a season.
  - [F1Calendar._get_fallback_calendar](F1Calendar._get_fallback_calendar.md) method: Fallback calendar when FastF1 unavailable.
  - [F1Calendar.get_race_by_number](F1Calendar.get_race_by_number.md) method: Get race info by race number.
  - [F1Calendar.get_race_by_name](F1Calendar.get_race_by_name.md) method: Get race info by GP name.
  - [F1Calendar.get_upcoming_races](F1Calendar.get_upcoming_races.md) method: Get upcoming races within specified days.
  - [F1Calendar.get_next_race](F1Calendar.get_next_race.md) method: Get the next race after reference date.
  - [F1Calendar.is_race_weekend](F1Calendar.is_race_weekend.md) method: Check if date falls on a race weekend.
  - [F1Calendar.get_current_race_weekend](F1Calendar.get_current_race_weekend.md) method: Get race info if currently on a race weekend.
  - [F1Calendar.format_race_info](F1Calendar.format_race_info.md) method: Format race info for display.
- [get_calendar](get_calendar.md) function: Get singleton calendar instance.
- [get_upcoming_races](get_upcoming_races.md) function: Get upcoming races. See F1Calendar.get_upcoming_races.
- [get_next_race](get_next_race.md) function: Get next race. See F1Calendar.get_next_race.
- [get_race_by_number](get_race_by_number.md) function: Get race by number. See F1Calendar.get_race_by_number.
- [get_race_by_name](get_race_by_name.md) function: Get race by name. See F1Calendar.get_race_by_name.
- [is_race_weekend](is_race_weekend.md) function: Check if it's a race weekend. See F1Calendar.is_race_weekend.

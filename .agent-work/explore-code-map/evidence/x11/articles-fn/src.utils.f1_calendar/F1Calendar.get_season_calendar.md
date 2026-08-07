# src.utils.f1_calendar:F1Calendar.get_season_calendar
method, src/utils/f1_calendar.py:54, 75 lines

```python
def get_season_calendar(self, season: int, force_refresh: bool = False) -> List[RaceInfo]
```

Get full calendar for a season.

Args:
    season: Season year
    force_refresh: Force reload even if cached

Returns:
    List of RaceInfo for all races in season

calls internal: F1Calendar._get_fallback_calendar, RaceInfo
calls cross-module: src.utils.constants:SPRINT_WEEKENDS.get
calls stdlib: builtins.int, builtins.len
calls third-party: fastf1.get_event_schedule
reads internal: F1Calendar._cache x3, logger x2
reads cross-module: src.utils.constants:SPRINT_WEEKENDS
reads stdlib: builtins.Exception
reads third-party: fastf1 (module)
writes internal: F1Calendar._cache[]
unresolved: 15 calls (dispatch-unknown-base)

referenced by: 5 sites, this module only

# src.utils.f1_calendar:F1Calendar._get_fallback_calendar
method, src/utils/f1_calendar.py:130, 28 lines

```python
def _get_fallback_calendar(self, season: int) -> List[RaceInfo]
```

Fallback calendar when FastF1 unavailable.

Returns race info without dates.

calls internal: RaceInfo
calls cross-module: src.utils.constants:F1_CALENDARS.get, src.utils.constants:SPRINT_WEEKENDS.get
calls stdlib: builtins.enumerate
reads internal: logger
reads cross-module: src.utils.constants:F1_CALENDARS, src.utils.constants:SPRINT_WEEKENDS
reads stdlib: datetime.datetime, datetime.datetime.min
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

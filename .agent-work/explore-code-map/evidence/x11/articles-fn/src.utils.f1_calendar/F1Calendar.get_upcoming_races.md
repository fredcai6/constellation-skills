# src.utils.f1_calendar:F1Calendar.get_upcoming_races
method, src/utils/f1_calendar.py:200, 41 lines

```python
def get_upcoming_races(self, season: int, days_ahead: int = 7, reference_date: Optional[datetime] = None) -> List[RaceInfo]
```

Get upcoming races within specified days.

Args:
    season: Season year
    days_ahead: Number of days to look ahead
    reference_date: Reference date (default: now)

Returns:
    List of RaceInfo for upcoming races

calls internal: F1Calendar.get_season_calendar
calls stdlib: builtins.hasattr x2, builtins.sorted, datetime.datetime.now
reads stdlib: datetime.datetime x2, datetime.datetime.min
writes internal: F1Calendar.get_upcoming_races.reference_date
unresolved: 3 calls (dispatch-unknown-base), 6 reads (dispatch-unknown-base), 1 reads (unbound-name)

referenced by: 1 sites, this module only

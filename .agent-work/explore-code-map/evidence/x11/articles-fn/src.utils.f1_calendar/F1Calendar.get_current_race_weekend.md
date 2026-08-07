# src.utils.f1_calendar:F1Calendar.get_current_race_weekend
method, src/utils/f1_calendar.py:295, 33 lines

```python
def get_current_race_weekend(self, season: int, check_date: Optional[datetime] = None) -> Optional[RaceInfo]
```

Get race info if currently on a race weekend.

Args:
    season: Season year
    check_date: Date to check (default: now)

Returns:
    RaceInfo if on race weekend, None otherwise

calls internal: F1Calendar._naive_datetime x2, F1Calendar.get_season_calendar
calls stdlib: datetime.datetime.now
reads stdlib: datetime.datetime x2, datetime.datetime.min
writes internal: F1Calendar.get_current_race_weekend.check_date
unresolved: 3 reads (dispatch-unknown-base)

referenced by: none found (scripts/ and tests/ not indexed)

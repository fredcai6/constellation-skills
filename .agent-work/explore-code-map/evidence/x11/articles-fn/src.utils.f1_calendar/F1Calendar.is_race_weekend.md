# src.utils.f1_calendar:F1Calendar.is_race_weekend
method, src/utils/f1_calendar.py:260, 34 lines

```python
def is_race_weekend(self, season: int, check_date: Optional[datetime] = None) -> bool
```

Check if date falls on a race weekend.

Args:
    season: Season year
    check_date: Date to check (default: now)

Returns:
    True if it's a race weekend

calls internal: F1Calendar._naive_datetime x2, F1Calendar.get_season_calendar
calls stdlib: datetime.datetime.now
reads stdlib: datetime.datetime x2, datetime.datetime.min
writes internal: F1Calendar.is_race_weekend.check_date
unresolved: 3 reads (dispatch-unknown-base)

referenced by: none found (scripts/ and tests/ not indexed)

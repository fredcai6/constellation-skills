# src.utils.f1_calendar:F1Calendar.get_next_race
method, src/utils/f1_calendar.py:242, 17 lines

```python
def get_next_race(self, season: int, reference_date: Optional[datetime] = None) -> Optional[RaceInfo]
```

Get the next race after reference date.

Args:
    season: Season year
    reference_date: Reference date (default: now)

Returns:
    Next RaceInfo or None if season is over

calls internal: F1Calendar.get_upcoming_races

referenced by: none found (scripts/ and tests/ not indexed)

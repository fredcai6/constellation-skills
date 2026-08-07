# src.utils.f1_calendar:F1Calendar.get_race_by_number
method, src/utils/f1_calendar.py:159, 16 lines

```python
def get_race_by_number(self, season: int, race_number: int) -> Optional[RaceInfo]
```

Get race info by race number.

Args:
    season: Season year
    race_number: Race number (1-indexed)

Returns:
    RaceInfo if found, None otherwise

calls internal: F1Calendar.get_season_calendar
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found (scripts/ and tests/ not indexed)

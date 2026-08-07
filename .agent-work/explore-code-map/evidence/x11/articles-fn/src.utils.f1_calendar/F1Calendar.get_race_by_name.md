# src.utils.f1_calendar:F1Calendar.get_race_by_name
method, src/utils/f1_calendar.py:176, 23 lines

```python
def get_race_by_name(self, season: int, gp_name: str) -> Optional[RaceInfo]
```

Get race info by GP name.

Args:
    season: Season year
    gp_name: Grand Prix name (e.g., "Monaco", "British")

Returns:
    RaceInfo if found, None otherwise

calls internal: F1Calendar.get_season_calendar
unresolved: 4 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found (scripts/ and tests/ not indexed)

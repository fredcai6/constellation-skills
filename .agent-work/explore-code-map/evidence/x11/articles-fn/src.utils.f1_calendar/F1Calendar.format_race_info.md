# src.utils.f1_calendar:F1Calendar.format_race_info
method, src/utils/f1_calendar.py:329, 24 lines

```python
def format_race_info(self, race: RaceInfo) -> str
```

Format race info for display.

Args:
    race: RaceInfo to format

Returns:
    Formatted string

reads internal: RaceInfo.quali_date x2, RaceInfo.race_date x2, RaceInfo.circuit_name, RaceInfo.country, RaceInfo.gp_name, RaceInfo.is_sprint_weekend, RaceInfo.race_number, RaceInfo.season
reads stdlib: datetime.datetime, datetime.datetime.min
unresolved: 2 calls (chained-attribute), 7 calls (dispatch-unknown-base)

referenced by: none found (scripts/ and tests/ not indexed)

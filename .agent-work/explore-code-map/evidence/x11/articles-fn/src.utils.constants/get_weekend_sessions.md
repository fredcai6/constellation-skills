# src.utils.constants:get_weekend_sessions
function, src/utils/constants.py:336, 16 lines

```python
def get_weekend_sessions(year: int, gp_name: str) -> List[str]
```

Get session types for a specific Grand Prix weekend.

Args:
    year: Season year
    gp_name: Grand Prix name

Returns:
    List of session types for that weekend

calls internal: is_sprint_weekend
reads internal: LEGACY_SPRINT_WEEKEND_SESSIONS, LEGACY_SPRINT_YEARS, NORMAL_WEEKEND_SESSIONS, SPRINT_WEEKEND_SESSIONS
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites in 1 modules (src.data.collector)

# scripts.apply_lessons_delta:_stamp_date
function, scripts/apply_lessons_delta.py:342, 5 lines

```python
def _stamp_date(stamp: str) -> str
```

Extract the ISO date from a "YYYY-MM-DD (work-id)" stamp for same-epoch

comparison. A bare token like "none" (unset last-confirmed) returns itself and
never matches a real date.

unresolved: 1 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only

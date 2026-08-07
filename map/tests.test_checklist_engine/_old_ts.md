# tests.test_checklist_engine:_old_ts
function, tests/test_checklist_engine.py:630, 4 lines

```python
def _old_ts(seconds_ago)
```

An ISO-8601 timestamp `seconds_ago` in the past (for stale-lease tests).

calls stdlib: datetime.datetime.now, datetime.timedelta
reads stdlib: datetime.datetime, datetime.timezone, datetime.timezone.utc
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 10 sites, this module only

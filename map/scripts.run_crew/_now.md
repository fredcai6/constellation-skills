# scripts.run_crew:_now
function, scripts/run_crew.py:74, 4 lines

```python
def _now() -> str
```

Current UTC time as an ISO-8601 string. Monkeypatch in tests to control

started_at/heartbeat/completed_at timestamps.

calls stdlib: datetime.datetime.now
reads stdlib: datetime.datetime, datetime.timezone, datetime.timezone.utc
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 6 sites, this module only

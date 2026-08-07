# scripts.checklist_engine:_now
function, scripts/checklist_engine.py:140, 4 lines

```python
def _now() -> str
```

Current UTC time as an ISO-8601 string. The single module-level time

hook: monkeypatch this in tests to control claim/heartbeat timestamps.

calls stdlib: datetime.datetime.now
reads stdlib: datetime.datetime, datetime.timezone, datetime.timezone.utc
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 10 sites, this module only

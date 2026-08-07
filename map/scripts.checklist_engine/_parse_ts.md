# scripts.checklist_engine:_parse_ts
function, scripts/checklist_engine.py:146, 10 lines

```python
def _parse_ts(value: str) -> datetime
```

Parse an ISO-8601 timestamp, tolerating a trailing 'Z'. Returns a

timezone-aware datetime (assumes UTC when no offset is present).

calls stdlib: datetime.datetime.fromisoformat
reads stdlib: datetime.datetime, datetime.timezone, datetime.timezone.utc
unresolved: 3 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only

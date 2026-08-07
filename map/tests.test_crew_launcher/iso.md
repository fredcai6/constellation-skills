# tests.test_crew_launcher:iso
function, tests/test_crew_launcher.py:13, 4 lines

```python
def iso(ts: float) -> str
```

ISO-8601 UTC string for a POSIX timestamp — used to build `started_at`

values relative to a controlled file mtime.

calls stdlib: datetime.datetime.fromtimestamp
reads stdlib: datetime.datetime, datetime.timezone, datetime.timezone.utc
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 10 sites, this module only

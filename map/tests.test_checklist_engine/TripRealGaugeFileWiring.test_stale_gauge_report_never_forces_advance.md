# tests.test_checklist_engine:TripRealGaugeFileWiring.test_stale_gauge_report_never_forces_advance
method, tests/test_checklist_engine.py:3762, 8 lines

```python
def test_stale_gauge_report_never_forces_advance(self)
```

HOLE: no docstring

calls internal: TripRealGaugeFileWiring.assertEqual x2, TripRealGaugeFileWiring._spine, TripRealGaugeFileWiring._write_gauge
calls stdlib: builtins.str, datetime.datetime.now, datetime.timedelta, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x3
reads stdlib: datetime.datetime, datetime.timezone, datetime.timezone.utc, tempfile (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found

# tests.test_checklist_engine:TripRealGaugeFileWiring.test_stale_gauge_reads_none_and_never_forces
method, tests/test_checklist_engine.py:3601, 10 lines

```python
def test_stale_gauge_reads_none_and_never_forces(self)
```

HOLE: no docstring

calls internal: TripRealGaugeFileWiring.assertEqual x2, TripRealGaugeFileWiring._spine, TripRealGaugeFileWiring._write_gauge
calls stdlib: builtins.min, builtins.str, datetime.datetime.now, datetime.timedelta, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x4
reads stdlib: datetime.datetime, datetime.timezone, datetime.timezone.utc, tempfile (module)
unresolved: 5 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

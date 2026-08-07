# tests.test_checklist_engine:TripRealGaugeFileWiring.test_stale_rejected_gauge_reports_raw_facts_on_current
method, tests/test_checklist_engine.py:3745, 16 lines

```python
def test_stale_rejected_gauge_reports_raw_facts_on_current(self)
```

HOLE: no docstring

calls internal: TripRealGaugeFileWiring.assertIn x2, TripRealGaugeFileWiring.assertNotIn x2, TripRealGaugeFileWiring._spine, TripRealGaugeFileWiring._write_gauge, TripRealGaugeFileWiring.assertEqual
calls stdlib: builtins.str, contextlib.redirect_stdout, datetime.datetime.now, datetime.timedelta, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x2
reads stdlib: contextlib (module), datetime.datetime, datetime.timezone, datetime.timezone.utc, io (module), tempfile (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found

# tests.test_checklist_engine:TripRealGaugeFileWiring.test_fresh_soft_gauge_advises_on_current_but_advance_passes
method, tests/test_checklist_engine.py:3670, 15 lines

```python
def test_fresh_soft_gauge_advises_on_current_but_advance_passes(self)
```

HOLE: no docstring

calls internal: TripRealGaugeFileWiring.assertEqual x2, TripRealGaugeFileWiring.assertIn x2, TripRealGaugeFileWiring._spine, TripRealGaugeFileWiring._write_gauge
calls stdlib: builtins.str x2, contextlib.redirect_stdout, datetime.datetime.now, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x4
reads stdlib: contextlib (module), datetime.datetime, datetime.timezone, datetime.timezone.utc, io (module), tempfile (module)
unresolved: 7 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

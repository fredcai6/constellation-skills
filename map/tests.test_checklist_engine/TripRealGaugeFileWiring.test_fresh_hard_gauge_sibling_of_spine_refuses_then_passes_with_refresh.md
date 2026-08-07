# tests.test_checklist_engine:TripRealGaugeFileWiring.test_fresh_hard_gauge_sibling_of_spine_refuses_then_passes_with_refresh
method, tests/test_checklist_engine.py:3579, 21 lines

```python
def test_fresh_hard_gauge_sibling_of_spine_refuses_then_passes_with_refresh(self)
```

HOLE: no docstring

calls internal: TripRealGaugeFileWiring.assertEqual x5, TripRealGaugeFileWiring._spine, TripRealGaugeFileWiring._write_gauge, TripRealGaugeFileWiring.assertIn
calls stdlib: builtins.str x3, builtins.min, contextlib.redirect_stderr, datetime.datetime.now, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x7
reads stdlib: contextlib (module), datetime.datetime, datetime.timezone, datetime.timezone.utc, io (module), tempfile (module)
unresolved: 9 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

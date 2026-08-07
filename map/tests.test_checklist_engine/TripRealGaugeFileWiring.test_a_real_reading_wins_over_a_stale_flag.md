# tests.test_checklist_engine:TripRealGaugeFileWiring.test_a_real_reading_wins_over_a_stale_flag
method, tests/test_checklist_engine.py:3654, 15 lines

```python
def test_a_real_reading_wins_over_a_stale_flag(self)
```

A leftover flag must not shout over a live gauge — the reading is

the better signal whenever one exists.

calls internal: TripRealGaugeFileWiring._spine, TripRealGaugeFileWiring._write_gauge, TripRealGaugeFileWiring._write_uncalibrated_flag, TripRealGaugeFileWiring.assertNotIn
calls stdlib: builtins.max, builtins.str, contextlib.redirect_stdout, datetime.datetime.now, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x3
reads stdlib: contextlib (module), datetime.datetime, datetime.timezone, datetime.timezone.utc, io (module), tempfile (module)
unresolved: 5 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

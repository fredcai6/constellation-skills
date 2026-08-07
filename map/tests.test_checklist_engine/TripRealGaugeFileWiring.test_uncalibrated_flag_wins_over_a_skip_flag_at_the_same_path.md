# tests.test_checklist_engine:TripRealGaugeFileWiring.test_uncalibrated_flag_wins_over_a_skip_flag_at_the_same_path
method, tests/test_checklist_engine.py:3729, 15 lines

```python
def test_uncalibrated_flag_wins_over_a_skip_flag_at_the_same_path(self)
```

Priority order proven with REAL coexisting sidecars, not just

mocks: the uncalibrated flag (a standing defect) always wins.

calls internal: TripRealGaugeFileWiring._spine, TripRealGaugeFileWiring._write_skip_flag_sidecar, TripRealGaugeFileWiring._write_uncalibrated_flag, TripRealGaugeFileWiring.assertIn, TripRealGaugeFileWiring.assertNotIn
calls stdlib: builtins.str, contextlib.redirect_stdout, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x2
reads stdlib: contextlib (module), io (module), tempfile (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

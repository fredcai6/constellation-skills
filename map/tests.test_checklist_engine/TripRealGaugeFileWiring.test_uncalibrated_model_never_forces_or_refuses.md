# tests.test_checklist_engine:TripRealGaugeFileWiring.test_uncalibrated_model_never_forces_or_refuses
method, tests/test_checklist_engine.py:3644, 9 lines

```python
def test_uncalibrated_model_never_forces_or_refuses(self)
```

It is a missing instrument, not a full context — with no window we

cannot claim the context is either full or empty, so advance passes.

calls internal: TripRealGaugeFileWiring.assertEqual x2, TripRealGaugeFileWiring._spine, TripRealGaugeFileWiring._write_uncalibrated_flag
calls stdlib: builtins.str, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x3
reads stdlib: tempfile (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

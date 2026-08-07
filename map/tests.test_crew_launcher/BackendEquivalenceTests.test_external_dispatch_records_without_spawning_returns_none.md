# tests.test_crew_launcher:BackendEquivalenceTests.test_external_dispatch_records_without_spawning_returns_none
method, tests/test_crew_launcher.py:749, 19 lines

```python
def test_external_dispatch_records_without_spawning_returns_none(self)
```

HOLE: no docstring

calls internal: BackendEquivalenceTests.assertEqual x5, BackendEquivalenceTests.assertIsNone x2, fake_launch, result_rel, write_handoff
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x3
reads stdlib: builtins.dict, builtins.list, tempfile (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

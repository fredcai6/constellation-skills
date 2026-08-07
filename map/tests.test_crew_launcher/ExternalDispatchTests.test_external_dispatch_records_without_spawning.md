# tests.test_crew_launcher:ExternalDispatchTests.test_external_dispatch_records_without_spawning
method, tests/test_crew_launcher.py:299, 24 lines

```python
def test_external_dispatch_records_without_spawning(self)
```

HOLE: no docstring

calls internal: ExternalDispatchTests.assertEqual x6, ExternalDispatchTests.assertIsNone, fake_launch, result_rel, write_handoff
calls stdlib: builtins.len, builtins.str, contextlib.redirect_stdout, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x4
reads stdlib: contextlib (module), io (module), tempfile (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

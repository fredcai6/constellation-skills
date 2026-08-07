# tests.test_crew_launcher:BackendFlagRoutingTests.test_backend_external_records_without_spawning
method, tests/test_crew_launcher.py:917, 17 lines

```python
def test_backend_external_records_without_spawning(self)
```

HOLE: no docstring

calls internal: BackendFlagRoutingTests.assertEqual x4, BackendFlagRoutingTests._launch_argv, BackendFlagRoutingTests.assertIsNone, fake_launch, result_rel, write_handoff
calls stdlib: contextlib.redirect_stdout, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x4
reads stdlib: contextlib (module), io (module), tempfile (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

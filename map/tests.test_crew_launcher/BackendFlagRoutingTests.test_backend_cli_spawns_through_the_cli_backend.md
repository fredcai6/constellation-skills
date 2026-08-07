# tests.test_crew_launcher:BackendFlagRoutingTests.test_backend_cli_spawns_through_the_cli_backend
method, tests/test_crew_launcher.py:900, 16 lines

```python
def test_backend_cli_spawns_through_the_cli_backend(self)
```

HOLE: no docstring

calls internal: BackendFlagRoutingTests.assertEqual x4, BackendFlagRoutingTests._launch_argv, fake_launch, result_rel, write_handoff
calls stdlib: builtins.len, contextlib.redirect_stdout, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x4
reads stdlib: contextlib (module), io (module), tempfile (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

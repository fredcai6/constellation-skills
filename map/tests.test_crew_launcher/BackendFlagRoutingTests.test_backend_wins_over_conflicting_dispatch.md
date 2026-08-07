# tests.test_crew_launcher:BackendFlagRoutingTests.test_backend_wins_over_conflicting_dispatch
method, tests/test_crew_launcher.py:935, 17 lines

```python
def test_backend_wins_over_conflicting_dispatch(self)
```

--backend external overrides --dispatch spawn (explicit override wins).

calls internal: BackendFlagRoutingTests.assertEqual x3, BackendFlagRoutingTests._launch_argv, fake_launch, result_rel, write_handoff
calls stdlib: contextlib.redirect_stdout, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x4
reads stdlib: contextlib (module), io (module), tempfile (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

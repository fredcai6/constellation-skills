# tests.test_crew_launcher:BackendFlagRoutingTests.test_default_no_backend_flag_resolves_to_cli_without_autodetect
method, tests/test_crew_launcher.py:953, 17 lines

```python
def test_default_no_backend_flag_resolves_to_cli_without_autodetect(self)
```

No --backend + default --dispatch spawn -> cli, regardless of PATH

(byte-for-byte backward compatible: no silent auto-detection).

calls internal: BackendFlagRoutingTests.assertEqual x3, BackendFlagRoutingTests._launch_argv, fake_launch, result_rel, write_handoff
calls stdlib: builtins.len, contextlib.redirect_stdout, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x4
reads stdlib: contextlib (module), io (module), tempfile (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

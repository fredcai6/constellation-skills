# tests.test_crew_launcher:LaunchTests.test_duplicate_active_lock_is_refused
method, tests/test_crew_launcher.py:209, 22 lines

```python
def test_duplicate_active_lock_is_refused(self)
```

HOLE: no docstring

calls internal: LaunchTests.assertEqual, LaunchTests.assertIsNotNone, result_rel, write_handoff
calls stdlib: builtins.str, contextlib.redirect_stderr, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x4
reads stdlib: contextlib (module), io (module), tempfile (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found

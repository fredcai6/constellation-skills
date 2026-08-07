# tests.test_crew_launcher:ExternalDispatchTests.test_external_duplicate_active_lock_is_refused
method, tests/test_crew_launcher.py:337, 15 lines

```python
def test_external_duplicate_active_lock_is_refused(self)
```

HOLE: no docstring

calls internal: ExternalDispatchTests.assertEqual x2, result_rel, write_handoff
calls stdlib: io.StringIO x2, builtins.str, contextlib.redirect_stderr, contextlib.redirect_stdout, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x2
reads stdlib: contextlib (module) x2, io (module) x2, tempfile (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found

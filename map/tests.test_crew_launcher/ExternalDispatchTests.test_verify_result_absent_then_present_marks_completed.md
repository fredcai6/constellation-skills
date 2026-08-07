# tests.test_crew_launcher:ExternalDispatchTests.test_verify_result_absent_then_present_marks_completed
method, tests/test_crew_launcher.py:353, 28 lines

```python
def test_verify_result_absent_then_present_marks_completed(self)
```

HOLE: no docstring

calls internal: ExternalDispatchTests.assertEqual x4, result_rel, write_handoff
calls stdlib: builtins.str x3, contextlib.redirect_stdout x3, io.StringIO x3, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x7
reads stdlib: contextlib (module) x3, io (module) x3, tempfile (module)
unresolved: 9 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

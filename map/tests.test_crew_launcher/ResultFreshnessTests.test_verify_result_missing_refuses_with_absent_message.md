# tests.test_crew_launcher:ResultFreshnessTests.test_verify_result_missing_refuses_with_absent_message
method, tests/test_crew_launcher.py:450, 19 lines

```python
def test_verify_result_missing_refuses_with_absent_message(self)
```

HOLE: no docstring

calls internal: ResultFreshnessTests.assertEqual x2, ResultFreshnessTests.assertIn, result_rel, write_handoff
calls stdlib: io.StringIO x3, builtins.str x2, contextlib.redirect_stdout x2, contextlib.redirect_stderr, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x4
reads stdlib: contextlib (module) x3, io (module) x3, tempfile (module)
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found

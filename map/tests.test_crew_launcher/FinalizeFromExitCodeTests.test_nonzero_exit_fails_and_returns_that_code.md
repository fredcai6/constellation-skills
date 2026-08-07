# tests.test_crew_launcher:FinalizeFromExitCodeTests.test_nonzero_exit_fails_and_returns_that_code
method, tests/test_crew_launcher.py:673, 10 lines

```python
def test_nonzero_exit_fails_and_returns_that_code(self)
```

HOLE: no docstring

calls internal: FinalizeFromExitCodeTests.assertEqual x2, iso, write_result_with_mtime
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: FinalizeFromExitCodeTests.BASE x2, RC
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

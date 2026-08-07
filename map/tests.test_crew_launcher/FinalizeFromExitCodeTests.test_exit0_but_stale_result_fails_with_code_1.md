# tests.test_crew_launcher:FinalizeFromExitCodeTests.test_exit0_but_stale_result_fails_with_code_1
method, tests/test_crew_launcher.py:684, 12 lines

```python
def test_exit0_but_stale_result_fails_with_code_1(self)
```

HOLE: no docstring

calls internal: FinalizeFromExitCodeTests.assertEqual x2, FinalizeFromExitCodeTests.assertFalse, FinalizeFromExitCodeTests.assertTrue, iso, write_result_with_mtime
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: FinalizeFromExitCodeTests.BASE x2, RC
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

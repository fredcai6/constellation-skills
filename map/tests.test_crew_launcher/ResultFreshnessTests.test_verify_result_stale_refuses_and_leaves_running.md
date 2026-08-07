# tests.test_crew_launcher:ResultFreshnessTests.test_verify_result_stale_refuses_and_leaves_running
method, tests/test_crew_launcher.py:422, 27 lines

```python
def test_verify_result_stale_refuses_and_leaves_running(self)
```

--verify-result on a STALE leftover prints a STALE refusal, returns 1,

and leaves the entry running (its hold on the gate is not cleared).

calls internal: ResultFreshnessTests.assertEqual x2, ResultFreshnessTests.assertFalse, ResultFreshnessTests.assertIn, ResultFreshnessTests.assertTrue, result_rel, write_handoff, write_result_with_mtime
calls stdlib: io.StringIO x3, builtins.str x2, contextlib.redirect_stdout x2, contextlib.redirect_stderr, datetime.datetime.fromisoformat, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x6
reads stdlib: contextlib (module) x3, io (module) x3, datetime.datetime, tempfile (module)
unresolved: 9 calls (dispatch-unknown-base)

referenced by: none found

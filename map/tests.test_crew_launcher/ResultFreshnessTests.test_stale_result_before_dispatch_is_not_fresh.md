# tests.test_crew_launcher:ResultFreshnessTests.test_stale_result_before_dispatch_is_not_fresh
method, tests/test_crew_launcher.py:403, 6 lines

```python
def test_stale_result_before_dispatch_is_not_fresh(self)
```

HOLE: no docstring

calls internal: ResultFreshnessTests.assertFalse, iso, write_result_with_mtime
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: ResultFreshnessTests.BASE x2, RC
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

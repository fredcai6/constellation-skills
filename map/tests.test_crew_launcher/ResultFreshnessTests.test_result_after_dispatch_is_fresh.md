# tests.test_crew_launcher:ResultFreshnessTests.test_result_after_dispatch_is_fresh
method, tests/test_crew_launcher.py:396, 6 lines

```python
def test_result_after_dispatch_is_fresh(self)
```

HOLE: no docstring

calls internal: ResultFreshnessTests.assertTrue, iso, write_result_with_mtime
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: ResultFreshnessTests.BASE x2, RC
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

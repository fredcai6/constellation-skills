# tests.test_crew_launcher:ResultFreshnessTests.test_missing_file_is_not_fresh
method, tests/test_crew_launcher.py:389, 6 lines

```python
def test_missing_file_is_not_fresh(self)
```

HOLE: no docstring

calls internal: ResultFreshnessTests.assertFalse, iso
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC, ResultFreshnessTests.BASE
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

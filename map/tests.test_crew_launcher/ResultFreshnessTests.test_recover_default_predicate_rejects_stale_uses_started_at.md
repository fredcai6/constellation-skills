# tests.test_crew_launcher:ResultFreshnessTests.test_recover_default_predicate_rejects_stale_uses_started_at
method, tests/test_crew_launcher.py:491, 12 lines

```python
def test_recover_default_predicate_rejects_stale_uses_started_at(self)
```

HOLE: no docstring

calls internal: ResultFreshnessTests.assertTrue x2, iso x2, ResultFreshnessTests.assertFalse, result_rel, write_result_with_mtime
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: ResultFreshnessTests.BASE x3, REC
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

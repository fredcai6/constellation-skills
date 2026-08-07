# tests.test_crew_launcher:ResultFreshnessTests.test_launch_finding_only_stale_result_marks_failed
method, tests/test_crew_launcher.py:470, 20 lines

```python
def test_launch_finding_only_stale_result_marks_failed(self)
```

A spawn that exits 0 but leaves only a STALE prior-attempt result at the

path is `failed`, not `completed`.

calls internal: ResultFreshnessTests.assertEqual, ResultFreshnessTests.assertFalse, ResultFreshnessTests.assertNotEqual, ResultFreshnessTests.assertTrue, fake_launch, result_rel, write_handoff, write_result_with_mtime
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x2, ResultFreshnessTests.BASE
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

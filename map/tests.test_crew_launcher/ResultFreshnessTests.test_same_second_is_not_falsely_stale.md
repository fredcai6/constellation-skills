# tests.test_crew_launcher:ResultFreshnessTests.test_same_second_is_not_falsely_stale
method, tests/test_crew_launcher.py:410, 11 lines

```python
def test_same_second_is_not_falsely_stale(self)
```

Sub-second `started_at` after the file mtime within the SAME whole

second must still read fresh — the floor guards coarse mtime resolution.

calls internal: ResultFreshnessTests.assertTrue, iso, write_result_with_mtime
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: ResultFreshnessTests.BASE x2, RC
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

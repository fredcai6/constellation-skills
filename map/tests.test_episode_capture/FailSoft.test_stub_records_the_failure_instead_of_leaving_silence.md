# tests.test_episode_capture:FailSoft.test_stub_records_the_failure_instead_of_leaving_silence
method, tests/test_episode_capture.py:396, 14 lines

```python
def test_stub_records_the_failure_instead_of_leaving_silence(self)
```

A non-reading must be visibly distinct from an uncollected one. "No file"

means nobody started this step; "a file carrying `emit_error`" means the step
started and the record could not be taken.

calls internal: FailSoft.assertEqual x2, FailSoft.assertIn x2, FailSoft.assertIsNone, work_area
calls stdlib: json.loads, pathlib.Path, tempfile.TemporaryDirectory
reads internal: ec
reads stdlib: json (module), tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

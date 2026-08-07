# tests.test_episode_capture:Seam.test_seam_a_task_declaring_nothing_still_gets_a_manifest
method, tests/test_episode_capture.py:340, 8 lines

```python
def test_seam_a_task_declaring_nothing_still_gets_a_manifest(self)
```

An empty `files` list is a real reading: "this step was delivered nothing

declared". It must not be confused with a step that was never started.

calls internal: Seam.assertEqual x2, engine, work_area
calls stdlib: json.loads, pathlib.Path, tempfile.TemporaryDirectory
reads internal: cm
reads stdlib: json (module), tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

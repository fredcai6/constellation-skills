# tests.test_episode_capture:Seam.test_seam_a_refused_start_emits_nothing
method, tests/test_episode_capture.py:349, 8 lines

```python
def test_seam_a_refused_start_emits_nothing(self)
```

The manifest records delivery to a step that actually activated. A refused

verb activated nothing, so a manifest would be a false record.

calls internal: Seam.assertEqual, Seam.assertFalse, engine, work_area
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: cm
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

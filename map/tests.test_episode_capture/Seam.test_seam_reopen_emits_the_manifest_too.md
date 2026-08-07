# tests.test_episode_capture:Seam.test_seam_reopen_emits_the_manifest_too
method, tests/test_episode_capture.py:323, 16 lines

```python
def test_seam_reopen_emits_the_manifest_too(self)
```

`reopen` is the second and only other door to `in-progress`; a seam wired

to `start` alone would leave reworked gates unrecorded.

calls internal: Seam.assertEqual x2, Seam.assertFalse, Seam.assertTrue, engine, git_repo, work_area
calls stdlib: pathlib.Path x2, json.loads, tempfile.TemporaryDirectory
reads internal: cm
reads stdlib: json (module), tempfile (module)
unresolved: 5 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

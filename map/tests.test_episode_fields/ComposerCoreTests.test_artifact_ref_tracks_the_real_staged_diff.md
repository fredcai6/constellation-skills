# tests.test_episode_fields:ComposerCoreTests.test_artifact_ref_tracks_the_real_staged_diff
method, tests/test_episode_fields.py:245, 17 lines

```python
@unittest.skipUnless(GIT, 'git not available on PATH')
def test_artifact_ref_tracks_the_real_staged_diff(self)
```

HOLE: no docstring

calls internal: ComposerCoreTests.assertEqual x2, checklist x2, git x2, init_repo
calls stdlib: builtins.sorted, pathlib.Path, tempfile.TemporaryDirectory
reads internal: ec x2
reads stdlib: tempfile (module)
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found

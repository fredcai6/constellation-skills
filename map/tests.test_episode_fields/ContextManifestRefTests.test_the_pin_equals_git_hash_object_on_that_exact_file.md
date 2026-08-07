# tests.test_episode_fields:ContextManifestRefTests.test_the_pin_equals_git_hash_object_on_that_exact_file
method, tests/test_episode_fields.py:634, 9 lines

```python
@unittest.skipUnless(GIT, 'git not available on PATH')
def test_the_pin_equals_git_hash_object_on_that_exact_file(self)
```

HOLE: no docstring

calls internal: ContextManifestRefTests.assertEqual x2, ContextManifestRefTests.manifest
calls stdlib: builtins.str, subprocess.run
reads internal: ContextManifestRefTests.spine x2
reads stdlib: subprocess (module)
unresolved: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found

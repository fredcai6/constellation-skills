# tests.test_episode_capture:FailSoft.test_stub_does_not_overwrite_a_manifest_that_was_already_taken
method, tests/test_episode_capture.py:426, 10 lines

```python
def test_stub_does_not_overwrite_a_manifest_that_was_already_taken(self)
```

HOLE: no docstring

calls internal: FailSoft.assertEqual, git_repo, work_area
calls stdlib: pathlib.Path x3, tempfile.TemporaryDirectory
reads internal: ec x2
reads stdlib: tempfile (module)
unresolved: 5 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: none found

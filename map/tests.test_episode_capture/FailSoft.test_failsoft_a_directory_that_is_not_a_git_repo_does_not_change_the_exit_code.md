# tests.test_episode_capture:FailSoft.test_failsoft_a_directory_that_is_not_a_git_repo_does_not_change_the_exit_code
method, tests/test_episode_capture.py:383, 7 lines

```python
def test_failsoft_a_directory_that_is_not_a_git_repo_does_not_change_the_exit_code(self)
```

HOLE: no docstring

calls internal: FailSoft.assertEqual, FailSoft.assertIsNone, engine, work_area
calls stdlib: json.loads, pathlib.Path, tempfile.TemporaryDirectory
reads internal: cm
reads stdlib: json (module), tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

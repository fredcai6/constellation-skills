# tests.test_init_work_area:RepoRootPlaceholder.test_repo_root_is_json_safe_on_windows
method, tests/test_init_work_area.py:467, 8 lines

```python
def test_repo_root_is_json_safe_on_windows(self)
```

A backslash value would break instantiate_spine's own json.loads guard.

calls internal: RepoRootPlaceholder.assertNotIn, load
calls stdlib: json.loads, pathlib.Path, tempfile.TemporaryDirectory
reads stdlib: json (module), tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

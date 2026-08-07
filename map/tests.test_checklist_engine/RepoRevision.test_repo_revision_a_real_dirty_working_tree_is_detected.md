# tests.test_checklist_engine:RepoRevision.test_repo_revision_a_real_dirty_working_tree_is_detected
method, tests/test_checklist_engine.py:1096, 15 lines

```python
def test_repo_revision_a_real_dirty_working_tree_is_detected(self)
```

HOLE: no docstring

calls internal: RepoRevision._git x5, RepoRevision.assertEqual x2, RepoRevision.assertTrue
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x2
reads stdlib: tempfile (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found

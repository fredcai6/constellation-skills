# tests.test_checklist_engine:RepoRevision.test_repo_revision_dirty_matches_git_status_porcelain_non_emptiness_oracle
method, tests/test_checklist_engine.py:1075, 5 lines

```python
def test_repo_revision_dirty_matches_git_status_porcelain_non_emptiness_oracle(self)
```

HOLE: no docstring

calls internal: RepoRevision.assertEqual x2, RepoRevision._git
calls stdlib: builtins.bool
reads internal: E, ROOT
unresolved: 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found

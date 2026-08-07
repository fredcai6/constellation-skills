# tests.test_checklist_engine:RepoRevision
class, tests/test_checklist_engine.py:1056, 55 lines

```python
class RepoRevision(TestCase)
```

`repo_revision()` -- Tommy's doctrine-version stamp (#300 g5): HEAD commit

plus a dirty marker, both via the existing `_git()` subprocess helper.
Oracle-compared against real `git` output, the same pattern the manifest's
`rev()` blob-OID tests use against `git hash-object`.

- [_git](RepoRevision._git.md) method: HOLE: no docstring
- [test_repo_revision_commit_matches_git_rev_parse_head_oracle](RepoRevision.test_repo_revision_commit_matches_git_rev_parse_head_oracle.md) method: HOLE: no docstring
- [test_repo_revision_dirty_matches_git_status_porcelain_non_emptiness_oracle](RepoRevision.test_repo_revision_dirty_matches_git_status_porcelain_non_emptiness_oracle.md) method: HOLE: no docstring
- [test_repo_revision_shape_is_exactly_commit_and_dirty](RepoRevision.test_repo_revision_shape_is_exactly_commit_and_dirty.md) method: HOLE: no docstring
- [test_repo_revision_a_non_git_directory_yields_none_none_without_raising](RepoRevision.test_repo_revision_a_non_git_directory_yields_none_none_without_raising.md) method: HOLE: no docstring
- [test_repo_revision_base_dir_none_falls_back_to_process_cwd](RepoRevision.test_repo_revision_base_dir_none_falls_back_to_process_cwd.md) method: HOLE: no docstring
- [test_repo_revision_a_real_dirty_working_tree_is_detected](RepoRevision.test_repo_revision_a_real_dirty_working_tree_is_detected.md) method: HOLE: no docstring

referenced by: none found

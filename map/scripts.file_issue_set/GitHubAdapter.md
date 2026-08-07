# scripts.file_issue_set:GitHubAdapter
class, scripts/file_issue_set.py:184, 46 lines

```python
class GitHubAdapter(FilingAdapter)
```

The shipped, GitHub-first adapter. Shells out to `gh`; finds an existing

item by searching for its embedded key marker so a crash re-run adopts
rather than duplicates. Not exercised by the offline test suite (no
network); the markdown adapter proves the idempotency contract.

- [__init__](GitHubAdapter.__init__.md) method: HOLE: no docstring
- [_gh](GitHubAdapter._gh.md) method: HOLE: no docstring
- [_find](GitHubAdapter._find.md) method: HOLE: no docstring
- [_create](GitHubAdapter._create.md) method: HOLE: no docstring
- [find_epic](GitHubAdapter.find_epic.md) method: HOLE: no docstring
- [create_epic](GitHubAdapter.create_epic.md) method: HOLE: no docstring
- [find_issue](GitHubAdapter.find_issue.md) method: HOLE: no docstring
- [create_issue](GitHubAdapter.create_issue.md) method: HOLE: no docstring

reads stdlib: builtins.str x20, builtins.dict x2, builtins.tuple x2, builtins.list

referenced by: 1 sites, this module only

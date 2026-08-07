# scripts.file_issue_set:build_adapter
function, scripts/file_issue_set.py:232, 11 lines

```python
def build_adapter(tracker: str, dest: str | None, repo: str | None) -> FilingAdapter
```

HOLE: no docstring

calls internal: GitHubAdapter, MarkdownAdapter
calls stdlib: pathlib.Path
calls third-party: verify_issue_set.IssueSetError x3

referenced by: 1 sites, this module only

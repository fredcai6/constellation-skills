# scripts.collect_feedback:file_issues
function, scripts/collect_feedback.py:548, 15 lines

```python
def file_issues(merged: Hits, *, inbox_path: Path, filer=gh_file_issue, include_singles: bool = False, confirm: bool = False, labels=(), repo: str | None = None) -> dict
```

Thin wrapper over `sync_issues` for callers/tests that only file.

calls internal: sync_issues

referenced by: none found

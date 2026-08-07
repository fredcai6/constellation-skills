# scripts.file_issue_set:GitHubAdapter._find
method, scripts/file_issue_set.py:204, 8 lines

```python
def _find(self, key: str) -> str | None
```

HOLE: no docstring

calls internal: GitHubAdapter._gh, key_marker
calls stdlib: json.loads
reads stdlib: json (module) x2, json.JSONDecodeError

referenced by: 2 sites, this module only

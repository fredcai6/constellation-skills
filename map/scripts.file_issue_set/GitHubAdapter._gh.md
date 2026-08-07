# scripts.file_issue_set:GitHubAdapter._gh
method, scripts/file_issue_set.py:194, 9 lines

```python
def _gh(self, args: list[str]) -> str
```

HOLE: no docstring

calls stdlib: builtins.RuntimeError, subprocess.run
reads internal: GitHubAdapter.repo x2
reads stdlib: os (module), os.environ, subprocess (module)
unresolved: 3 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only

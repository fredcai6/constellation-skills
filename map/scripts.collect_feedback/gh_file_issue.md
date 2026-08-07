# scripts.collect_feedback:gh_file_issue
function, scripts/collect_feedback.py:406, 12 lines

```python
def gh_file_issue(spec: dict, *, repo: str | None = None) -> dict
```

Default filer: open a GitHub issue via `gh`. Returns {number, url}.

calls stdlib: subprocess.run
reads stdlib: subprocess (module)
unresolved: 5 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only

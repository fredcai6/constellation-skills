# scripts.verify_issue_set:verify_edges
function, scripts/verify_issue_set.py:84, 20 lines

```python
def verify_edges(manifest: dict) -> None
```

Rule 2: at least one dependency edge across the set, and every edge

target names a known issue id (no dangling edge).

calls internal: _require x3
calls stdlib: builtins.str x2, builtins.isinstance
reads stdlib: builtins.list
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

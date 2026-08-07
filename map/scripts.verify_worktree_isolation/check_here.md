# scripts.verify_worktree_isolation:check_here
function, scripts/verify_worktree_isolation.py:89, 9 lines

```python
def check_here(actual_toplevel: str, expected: str) -> tuple[bool, str]
```

The pure --here decision: is the current worktree the expected one?

calls internal: normalize_path x2

referenced by: 1 sites, this module only

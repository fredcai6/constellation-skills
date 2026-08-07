# scripts.verify_worktree_isolation:_utf8_stdio
function, scripts/verify_worktree_isolation.py:36, 6 lines

```python
def _utf8_stdio() -> None
```

HOLE: no docstring

reads stdlib: sys (module) x2, builtins.AttributeError, builtins.OSError, sys.stderr, sys.stdout
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

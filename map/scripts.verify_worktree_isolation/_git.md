# scripts.verify_worktree_isolation:_git
function, scripts/verify_worktree_isolation.py:100, 8 lines

```python
def _git(*args: str) -> str
```

Run a read-only git command and return its stripped stdout.

calls stdlib: builtins.RuntimeError, subprocess.run
reads stdlib: subprocess (module)
unresolved: 3 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only

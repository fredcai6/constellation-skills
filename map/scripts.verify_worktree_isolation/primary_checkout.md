# scripts.verify_worktree_isolation:primary_checkout
function, scripts/verify_worktree_isolation.py:114, 6 lines

```python
def primary_checkout() -> str
```

The main checkout: the parent of the common git dir. Ordering-independent,

unlike trusting the first `git worktree list` entry (undefined for a bare
repo).

calls internal: _git
calls stdlib: os.path.abspath, os.path.dirname
reads stdlib: os (module) x2, os.path x2

referenced by: 1 sites, this module only

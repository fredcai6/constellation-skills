# scripts.verify_worktree_isolation:normalize_path
function, scripts/verify_worktree_isolation.py:47, 6 lines

```python
def normalize_path(p: str) -> str
```

Canonicalize a path for comparison: an absolute real path (symlinks and

Windows junctions resolved by realpath) with drive-case and `/` vs `\`
separators folded by normcase. Two strings naming the same location compare
equal after this.

calls stdlib: os.path.normcase, os.path.realpath
reads stdlib: os (module) x2, os.path x2

referenced by: 5 sites, this module only

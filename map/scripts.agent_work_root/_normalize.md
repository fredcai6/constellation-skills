# scripts.agent_work_root:_normalize
function, scripts/agent_work_root.py:52, 4 lines

```python
def _normalize(path: str) -> str
```

Canonical form for comparison: absolute real path, drive-case and separators

folded — same idiom as `verify_worktree_isolation.normalize_path`.

calls stdlib: os.path.normcase, os.path.realpath
reads stdlib: os (module) x2, os.path x2

referenced by: 2 sites, this module only

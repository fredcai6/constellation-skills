# scripts.check_skill_freshness:update_baseline
function, scripts/check_skill_freshness.py:129, 20 lines

```python
def update_baseline(project_root: Path, skills_root: Path) -> int
```

HOLE: no docstring

calls internal: _hash, _load_manifest
calls stdlib: json.dumps, shutil.copy2
reads stdlib: json (module), shutil (module)
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

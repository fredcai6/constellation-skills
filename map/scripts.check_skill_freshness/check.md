# scripts.check_skill_freshness:check
function, scripts/check_skill_freshness.py:90, 37 lines

```python
def check(project_root: Path, skills_root: Path) -> list[dict[str, str]]
```

HOLE: no docstring

calls internal: _normalized_hash x3, _load_manifest
reads stdlib: builtins.str x2, builtins.dict, builtins.list
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

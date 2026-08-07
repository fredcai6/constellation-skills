# scripts.grade_lint:load_id_universe
function, scripts/grade_lint.py:622, 8 lines

```python
def load_id_universe(path: Path) -> set[str]
```

HOLE: no docstring

calls internal: extract_plan_ids
calls stdlib: json.loads
reads stdlib: json (module) x2, json.JSONDecodeError
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

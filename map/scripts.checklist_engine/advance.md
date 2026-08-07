# scripts.checklist_engine:advance
function, scripts/checklist_engine.py:1736, 61 lines

```python
def advance(cl: dict, iid: str, from_child: str | None = None, base_dir: Path | None = None, why: str | None = None, mechanical: bool = False) -> str
```

HOLE: no docstring

calls internal: EngineError x7, _append_why x2, _check_condition, _condition_kind, attach, task
calls stdlib: builtins.any, builtins.bool, json.loads, pathlib.Path
reads internal: GATED
reads stdlib: json (module)
unresolved: 12 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

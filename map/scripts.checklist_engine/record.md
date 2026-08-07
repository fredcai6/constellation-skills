# scripts.checklist_engine:record
function, scripts/checklist_engine.py:1799, 30 lines

```python
def record(cl: dict, iid: str, result: str, finding: str | None, base_dir: Path | None = None) -> str
```

HOLE: no docstring

calls internal: EngineError x3, _check_condition, _condition_kind, task
reads internal: SURVEY
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

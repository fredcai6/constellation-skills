# scripts.checklist_engine:start
function, scripts/checklist_engine.py:1703, 31 lines

```python
def start(cl: dict, iid: str, base_dir: Path | None = None) -> str
```

HOLE: no docstring

calls internal: EngineError x3, active_id x2, _check_condition, _condition_kind, task
calls third-party: episode_capture.emit_step_manifest
reads internal: GATED
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

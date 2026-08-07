# scripts.checklist_engine:heartbeat
function, scripts/checklist_engine.py:1000, 13 lines

```python
def heartbeat(cl: dict, session_id: str) -> str
```

Refresh the active lease's `last_heartbeat`. Only the owning session may

heartbeat; refuses if there is no active lease or the id mismatches.

calls internal: EngineError x2, _active_lease, _now
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

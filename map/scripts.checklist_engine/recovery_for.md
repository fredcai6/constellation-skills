# scripts.checklist_engine:recovery_for
function, scripts/checklist_engine.py:335, 122 lines

```python
def recovery_for(exc: 'EngineError', cl: dict) -> str
```

A recovery line naming a runnable exit command for a state-caused

`EngineError`, or ``""`` when the refusal carries no `task_id` (not every
refusal is state-caused — a missing/malformed argument, an unowned lease,
etc. are left as their existing bare message).

calls internal: _next_verbs, active_id
reads internal: _RECOVERY_TAIL x11, GATED x3
unresolved: 13 calls (dispatch-unknown-base), 14 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

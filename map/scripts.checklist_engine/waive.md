# scripts.checklist_engine:waive
function, scripts/checklist_engine.py:2321, 46 lines

```python
def waive(cl: dict, iid: str, cond_id: str, which: str, authority: str, reason: str | None, forced: bool = False) -> str
```

Human override: explicitly satisfy a condition by waiver, auditable.

Refused unless the condition's `override_policy.allowed` is true — unless an
explicit high-friction `--force` is given (force still demands authority +
reason and is recorded as a forced override). The engine does not judge
whether a waiver is wise; it records authority and refuses accidental use.

calls internal: EngineError x4, _new_evidence_id, task
calls stdlib: builtins.bool
writes internal: waive.reason
unresolved: 8 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

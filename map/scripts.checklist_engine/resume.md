# scripts.checklist_engine:resume
function, scripts/checklist_engine.py:1881, 36 lines

```python
def resume(cl: dict, iid: str, reason: str, note: str | None = None) -> str
```

Move a resolved `block` forward: return a blocked gate to the status it held

BEFORE it was blocked (recorded by `block` as status_detail.prior_status), so the
delegate float-then-resume pattern has a sanctioned path — before this, the only
exit from a block was `skip` (OBE). Clears the blocked markers, records the
resolution, and drops the gate's entry from the bubbled `blockers` list.

Restores ONLY a `pending`/`in-progress` prior status. A blocked gate with no
restorable prior (a reopen rework-cap escalation, or a legacy block predating
this verb) is REFUSED — resuming a cap-escalated gate would bypass the rework cap.
Refuses a gate that is not `blocked` and an empty reason.

calls internal: EngineError x3, task
calls stdlib: builtins.isinstance
reads stdlib: builtins.list
writes internal: resume.cl[]
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

# scripts.checklist_engine:reopen
function, scripts/checklist_engine.py:1940, 72 lines

```python
def reopen(cl: dict, iid: str, reason: str, cap: int | None = None, base_dir: Path | None = None) -> str
```

Reopen a complete gate for rework. Increments `rework_count`, escalates

(blocks + bubbles, no reopen) when the cap is exceeded, and on the success
path resets the gate's postconditions and CASCADES downstream: every later
gate that is `complete`/`in-progress` is reset to `pending` (both pre- and
postconditions cleared, evidence superseded, `status_detail.superseded_by_reopen`
stamped). `skipped`/`blocked` downstream gates are deliberate OBE/bubble states
and are left untouched. Evidence on the target and each cascaded gate is
superseded (retained, not deleted) so a reopened gate cannot re-pass from a
stale approval — the bug this cascade fixes.

calls internal: _reset_conditions x3, EngineError x2, _append_reopen_marker x2, _supersede_evidence x2, rework_cap, task
calls third-party: episode_capture.emit_step_manifest
reads internal: GATED
reads stdlib: builtins.list, builtins.str
writes internal: reopen.cap
unresolved: 13 calls (dispatch-unknown-base), 2 writes (non-name-expr)

referenced by: 1 sites, this module only

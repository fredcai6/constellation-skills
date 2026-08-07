# scripts.checklist_engine:claim
function, scripts/checklist_engine.py:912, 86 lines

```python
def claim(cl: dict, session_id: str, claimed_by: str, worktree: str, config: dict, force: bool = False, reason: str | None = None) -> str
```

Claim ownership of the checklist for `session_id`.

- No existing/closed/stale lease: create a fresh active lease.
- Same `session_id` already active: idempotent resume; refresh heartbeat.
- A DIFFERENT active, non-stale lease: refuse unless `--force --reason`.
- `--force` takes over any lease, recording the prior session in
  `previous_session_id` and the `takeover_reason` (force needs a reason).

calls internal: EngineError x3, _is_stale x2, _now
calls stdlib: builtins.isinstance
reads stdlib: builtins.dict
writes internal: claim.cl[], claim.reason
unresolved: 14 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

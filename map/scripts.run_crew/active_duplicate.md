# scripts.run_crew:active_duplicate
function, scripts/run_crew.py:133, 18 lines

```python
def active_duplicate(entries: list[dict], work_id: str, gate: str, role: str, worktree: str) -> dict | None
```

The blocking duplicate, if any: an existing entry for the same

work-id/gate/role/worktree whose status is still active (`running`/
`resumable`) and which has NOT been abandoned. PURE — used both to refuse a
fresh launch and (by recover_crews) to report an active lock.

calls internal: is_abandoned
reads internal: ACTIVE_STATUSES
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

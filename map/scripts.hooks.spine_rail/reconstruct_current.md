# scripts.hooks.spine_rail:reconstruct_current
function, scripts/hooks/spine_rail.py:276, 29 lines

```python
def reconstruct_current(spine: dict) -> str
```

Rebuild the engine's `current` output from the state file (no subprocess).

Optional `LEASE active: ...` line, then `ACTIVE <aid> [<status>] -- <imp>`
or `DONE: no open items.` when every item is terminal.

calls internal: active_id
unresolved: 15 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

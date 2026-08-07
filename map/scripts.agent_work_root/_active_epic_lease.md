# scripts.agent_work_root:_active_epic_lease
function, scripts/agent_work_root.py:76, 32 lines

```python
def _active_epic_lease(main_checkout: str | os.PathLike[str]) -> bool
```

True iff the main checkout holds an ACTIVE Admiral epic lease.

Scans `<main_checkout>/.agent-work/*/spine.json` for an `engine_session` dict
with `status == "active"` AND `claimed_by == "admiral"` (case-insensitive,
stripped). No staleness gate — `last_heartbeat` is not consulted. Fully
defensive: an empty glob, or a `spine.json` that is missing, unreadable,
invalid JSON, non-dict, or lacking a dict `engine_session`, is skipped. Never
raises — any unexpected error scanning a file falls back to skipping it.

calls stdlib: builtins.isinstance x2, builtins.str x2, builtins.list, json.loads, pathlib.Path
reads stdlib: builtins.OSError x2, builtins.dict x2, builtins.ValueError, json (module)
unresolved: 9 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

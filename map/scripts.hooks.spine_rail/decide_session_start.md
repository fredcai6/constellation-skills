# scripts.hooks.spine_rail:decide_session_start
function, scripts/hooks/spine_rail.py:631, 67 lines

```python
def decide_session_start(data: dict, project_dir: Path) -> dict
```

HOLE: no docstring

calls internal: _foreign_worktree, _now_iso, _scan_active_spine, active_id, load_binding, load_spine, reconstruct_current, save_binding, session_view
calls stdlib: builtins.dict, builtins.len, builtins.str
reads stdlib: builtins.Exception
unresolved: 10 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

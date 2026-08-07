# scripts.install_constellation:add_hook_entry
function, scripts/install_constellation.py:795, 19 lines

```python
def add_hook_entry(settings: dict, entry: dict) -> bool
```

Append `entry` as a SIBLING in `hooks.PostToolUse`, in place. Never nests

inside an existing matcher block, never reorders what is already there, and
never removes anything -- including a stale governor entry, which is
reported rather than silently rewritten (no self-healing, by design).

Returns False when an identical command is already present.

calls internal: InstallError x2, governor_hook_commands
calls stdlib: builtins.isinstance x2, builtins.type x2
reads internal: HOOK_EVENT x2
reads stdlib: builtins.dict, builtins.list
unresolved: 3 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

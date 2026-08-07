# scripts.install_constellation:describe_hook_wiring
function, scripts/install_constellation.py:725, 36 lines

```python
def describe_hook_wiring(wiring: HookWiring) -> str
```

One reportable line. ASCII only -- this goes to a Windows console.

calls internal: extract_hook_script_path
calls stdlib: builtins.len x2, builtins.sorted
reads internal: HookWiring.settings_path x5, HookWiring.state x4, HOOK_EVENT x3, GAUGE_WRITER_HOOK_SCRIPT x2, HookWiring.undeterminable x2, HookWiring.unresolved x2, HookWiring.error, HookWiring.resolved, HookWiring.settings_exists, WIRING_STALE, WIRING_UNDETERMINABLE, WIRING_UNREADABLE, WIRING_WIRED
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

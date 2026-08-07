# scripts.install_constellation:detect_hook_wiring
function, scripts/install_constellation.py:681, 42 lines

```python
def detect_hook_wiring(settings_path: Path, *, env: Mapping[str, str]) -> HookWiring
```

Three-state and READ-ONLY -- opens nothing for writing and creates

nothing.

Classification is by RESOLVING each entry's script path against the
filesystem, never by string-matching the command. Under a string match a
moved, renamed, or uninstalled tree still reads as `wired`, which is exactly
the reassuring-failure shape this detector exists to prevent.

calls internal: HookWiring x3, _expand_env_tokens, extract_hook_script_path, governor_hook_commands
calls stdlib: builtins.tuple x3, builtins.str, json.loads, pathlib.Path
reads internal: WIRING_UNWIRED x2, WIRING_STALE, WIRING_UNDETERMINABLE, WIRING_UNREADABLE, WIRING_WIRED, _ENV_TOKEN_RE
reads stdlib: builtins.list x3, builtins.str x3, builtins.OSError, builtins.ValueError, json (module)
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

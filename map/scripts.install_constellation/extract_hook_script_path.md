# scripts.install_constellation:extract_hook_script_path
function, scripts/install_constellation.py:648, 7 lines

```python
def extract_hook_script_path(command: str) -> str | None
```

The gauge-writer script path a hook `command` string invokes, or None

when the command is not a Context Governor entry at all.

reads internal: _HOOK_SCRIPT_PATH_RE
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only

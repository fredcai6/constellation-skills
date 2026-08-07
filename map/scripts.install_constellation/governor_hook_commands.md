# scripts.install_constellation:governor_hook_commands
function, scripts/install_constellation.py:657, 22 lines

```python
def governor_hook_commands(settings: object) -> list[str]
```

Every PostToolUse `command` string that invokes a gauge writer hook,

flattened across matcher blocks. Deliberately tolerant of shapes it does
not expect: an odd settings.json is something to REPORT, never something to
raise on in the middle of an otherwise-fine install.

calls internal: extract_hook_script_path
calls stdlib: builtins.isinstance x6
reads internal: HOOK_EVENT
reads stdlib: builtins.dict x4, builtins.list x2, builtins.str x2
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

# scripts.hooks.gauge_writer_hook:main
function, scripts/hooks/gauge_writer_hook.py:668, 20 lines

```python
def main(argv, stdin_text) -> int
```

Single-purpose hook (PostToolUse only) -- no event-name dispatch is

needed; the settings.json wiring registers this script for PostToolUse
specifically (see docs/GAUGE_WRITER_HOOK.md). Always exits 0.

calls internal: handle_post_tool_use
calls stdlib: builtins.isinstance, json.loads, os.environ.get, os.getcwd, pathlib.Path
reads internal: _spine_rail x2
reads stdlib: builtins.Exception x2, os (module) x2, builtins.dict, json (module), os.environ
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

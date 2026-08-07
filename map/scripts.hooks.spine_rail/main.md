# scripts.hooks.spine_rail:main
function, scripts/hooks/spine_rail.py:702, 25 lines

```python
def main(argv, stdin_text) -> int
```

Dispatch by event name (argv[1]); print result JSON only if non-empty;

always exit 0. Wrapped: any exception -> print nothing, exit 0 (fail-open).

calls internal: decide_session_start, decide_stop, handle_post_tool_use, resolve_project_dir
calls stdlib: builtins.isinstance, builtins.len, builtins.print, json.dumps, json.loads
reads stdlib: builtins.Exception x2, json (module) x2, builtins.dict
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

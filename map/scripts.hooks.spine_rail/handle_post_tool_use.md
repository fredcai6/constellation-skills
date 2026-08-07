# scripts.hooks.spine_rail:handle_post_tool_use
function, scripts/hooks/spine_rail.py:405, 87 lines

```python
def handle_post_tool_use(data: dict, project_dir: Path) -> dict
```

Maintain the session->spine binding from engine claim/release commands.

One session_id can hold a binding into more than one distinct spine at
once (#202) -- the binding is keyed by the RESOLVED ABSOLUTE SPINE PATH
itself (`abs_spine`), not by worktree or cwd
(decision:key-binding-by-spine-path-not-worktree-or-cwd). A claim writes
only `binding[key][abs_spine]`, leaving any other abs_spine_path entries
for that key untouched; a release removes only that one entry.

The OUTER key is `binding_key(data)` (#419), not the bare `session_id`:
subagents share their parent's session_id, so keying on it alone piled
every crew claim under one key and left the gauge writer with no way to
tell whose reading it held. `binding_key` returning None means the acting
identity is unresolved -- bind NOTHING, write no entry at all.

PostToolUse NEVER blocks -- always returns {}.

calls internal: _extract_opt x2, save_binding x2, _extract_verb, _now_iso, _resolve_abs, _tokenize, binding_key, load_binding, load_nudges, save_nudges
calls stdlib: builtins.dict x2, builtins.any, builtins.str
reads stdlib: builtins.Exception
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

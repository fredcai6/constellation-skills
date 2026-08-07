# scripts.hooks.spine_rail:load_binding
function, scripts/hooks/spine_rail.py:114, 19 lines

```python
def load_binding(project_dir: Path) -> dict
```

Load `session_id -> {abs_spine_path: {spine, engine_session, worktree,

claimed_at}}`.

An old-shape (flat, pre-#202) entry under a session_id is treated as
ABSENT for that session_id -- fail-open, never a crash and never a silent
misinterpretation as a new-shape entry (decision:binding-schema-may-change).
No in-place migration: the file self-heals as sessions re-claim under the
new writer.

calls internal: _is_old_shape_binding_entry, _load_json_map, binding_path
calls stdlib: builtins.isinstance
reads stdlib: builtins.Exception, builtins.dict
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only

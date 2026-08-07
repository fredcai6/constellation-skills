# scripts.hooks.spine_rail:_is_old_shape_binding_entry
function, scripts/hooks/spine_rail.py:102, 10 lines

```python
def _is_old_shape_binding_entry(entry: dict) -> bool
```

True if `entry` looks like the OLD flat per-session binding value

(`{spine, engine_session, worktree}`) rather than the NEW nested
`{abs_spine_path: {spine, engine_session, worktree, claimed_at}}` map.

A `"spine"` key present DIRECTLY on `entry` is the old shape's signature --
the new shape's values are themselves dicts keyed by abs_spine_path, never
a literal `"spine"` key at this level.

referenced by: 1 sites, this module only

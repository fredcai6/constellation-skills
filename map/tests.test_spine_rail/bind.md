# tests.test_spine_rail:bind
function, tests/test_spine_rail.py:73, 14 lines

```python
def bind(project_dir, sid, spine_path, engine_session='eng-1', worktree=None)
```

Write a NEW-shape binding: one nested entry, keyed by spine_path, for

`sid`. Merges onto any existing bindings for `sid` (mirrors the real
claim writer's leave-siblings-untouched behavior) rather than clobbering.

calls stdlib: builtins.str x3, builtins.dict
reads internal: sr x2
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 18 sites, this module only

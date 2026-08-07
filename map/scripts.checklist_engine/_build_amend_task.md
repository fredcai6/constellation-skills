# scripts.checklist_engine:_build_amend_task
function, scripts/checklist_engine.py:2017, 21 lines

```python
def _build_amend_task(op: dict) -> dict
```

Build a full pending task from an `add` op, mirroring `append()`'s shape.

`preconditions`/`constraints` default to empty; `directives`/`child_checklist`
default to None. Deep-copied so the caller's op dict is never aliased into
canonical state.

calls stdlib: copy.deepcopy x4
reads stdlib: copy (module) x4
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

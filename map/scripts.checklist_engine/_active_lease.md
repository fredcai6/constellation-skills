# scripts.checklist_engine:_active_lease
function, scripts/checklist_engine.py:858, 7 lines

```python
def _active_lease(cl: dict) -> dict | None
```

The lease iff it is present and `status: active`; else None. A released

lease does not gate mutation.

calls stdlib: builtins.isinstance
reads stdlib: builtins.dict
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only

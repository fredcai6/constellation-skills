# scripts.checklist_engine:_condition_open
function, scripts/checklist_engine.py:1461, 5 lines

```python
def _condition_open(c: dict) -> bool
```

True iff the condition is NOT (yet) recorded as satisfied. Reads the

stored `satisfied` flag only — see the INV-2 sharp edge above; this is
never a live re-check.

calls stdlib: builtins.bool
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

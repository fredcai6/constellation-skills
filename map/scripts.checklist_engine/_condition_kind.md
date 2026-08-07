# scripts.checklist_engine:_condition_kind
function, scripts/checklist_engine.py:1452, 7 lines

```python
def _condition_kind(c: dict) -> str
```

The condition's check kind for display: the literal `check.kind`, or

"null" for a qualitative (`check: null`) condition. Never runs the check.

calls stdlib: builtins.isinstance
reads stdlib: builtins.dict
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 6 sites, this module only

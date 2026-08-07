# scripts.checklist_engine:_latest_why_record
function, scripts/checklist_engine.py:1082, 16 lines

```python
def _latest_why_record(cl: dict) -> dict | None
```

The live why-record: the newest `why_trail` entry that is a real (non-

mechanical) understanding AND has not been superseded by a later reopen of its
own gate. Returns the entry dict, or None when no live understanding exists.
A mechanical marker is never live (it carries no understanding).

calls stdlib: builtins.len x2, builtins.range x2, builtins.any
unresolved: 7 calls (dispatch-unknown-base)

referenced by: 4 sites, this module only

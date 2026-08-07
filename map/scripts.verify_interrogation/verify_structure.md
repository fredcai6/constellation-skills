# scripts.verify_interrogation:verify_structure
function, scripts/verify_interrogation.py:60, 33 lines

```python
def verify_structure(record: object) -> dict
```

The record's basic shape: a goal, a mode, and a non-empty typed question

list with unique ids and valid kind/status.

calls internal: _require x10, _nonempty x2
calls stdlib: builtins.isinstance x5, builtins.bool, builtins.enumerate, builtins.len, builtins.set, builtins.str
reads internal: VALID_KINDS x2, VALID_MODES x2, VALID_STATUSES x2
reads stdlib: builtins.dict x3, builtins.list x2, builtins.set, builtins.str
unresolved: 12 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

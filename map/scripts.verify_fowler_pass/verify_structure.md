# scripts.verify_fowler_pass:verify_structure
function, scripts/verify_fowler_pass.py:87, 29 lines

```python
def verify_structure(record: object) -> dict
```

The record's basic shape: a diff reference and a smell list with unique,

known smell names and valid verdicts.

calls internal: _require x8, _nonempty
calls stdlib: builtins.isinstance x5, builtins.bool, builtins.enumerate, builtins.len, builtins.set, builtins.str
reads internal: REQUIRED_SMELLS x2, VALID_VERDICTS x2
reads stdlib: builtins.dict x3, builtins.list x2, builtins.set, builtins.str
unresolved: 8 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

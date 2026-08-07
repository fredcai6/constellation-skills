# scripts.map_orient:receipt_problems
function, scripts/map_orient.py:565, 27 lines

```python
def receipt_problems(receipt: object, work_id: str) -> list[str]
```

PURE. Structural problems with a receipt; empty means well-formed.

calls internal: is_filler
calls stdlib: builtins.isinstance x3
reads internal: SCHEMA_VERSION x2, MODE_RESOLVED, MODE_UNRESOLVABLE_ROOT, ORIENT_MODES, RECEIPT_REQUIRED_FIELDS
reads stdlib: builtins.dict, builtins.int, builtins.list
unresolved: 18 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

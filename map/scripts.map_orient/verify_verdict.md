# scripts.map_orient:verify_verdict
function, scripts/map_orient.py:594, 12 lines

```python
def verify_verdict(receipt: object, work_id: str) -> tuple[str, int, list[str]]
```

PURE. (reserved first line, exit code, problems) for `verify-orientation`.

calls internal: exit_code_for x2, degraded_record_is_complete, missing_degraded_fields, receipt_problems
calls stdlib: builtins.isinstance
reads internal: EXIT_RECEIPT_UNUSABLE, MODE_RESOLVED, MODE_UNRESOLVABLE_ROOT, ORIENT_MODES, RECEIPT_MISSING
reads stdlib: builtins.dict
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 10 sites, this module only

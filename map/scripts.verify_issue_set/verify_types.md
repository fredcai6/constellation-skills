# scripts.verify_issue_set:verify_types
function, scripts/verify_issue_set.py:106, 14 lines

```python
def verify_types(manifest: dict) -> None
```

Rules 3 and 4: every issue typed HITL/AFK; HITL requires a hitl_reason.

calls internal: _require x2
calls stdlib: builtins.bool, builtins.str
reads internal: VALID_TYPES x2
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

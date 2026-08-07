# scripts.verify_diagnosis:verify_structure
function, scripts/verify_diagnosis.py:75, 26 lines

```python
def verify_structure(finding: object) -> dict
```

Rule 1: the loop's basic shape — symptom, altitude, oracle, status.

calls internal: _require x5, _nonempty x2
calls stdlib: builtins.isinstance x2
reads internal: VALID_ALTITUDES x2, VALID_STATUSES x2
reads stdlib: builtins.dict x2
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

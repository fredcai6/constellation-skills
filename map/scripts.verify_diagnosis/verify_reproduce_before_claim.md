# scripts.verify_diagnosis:verify_reproduce_before_claim
function, scripts/verify_diagnosis.py:123, 16 lines

```python
def verify_reproduce_before_claim(finding: dict) -> None
```

Rule 3 (THE RAIL): a confirmed cause must carry a named falsifier + an

observed reproduce/instrument result, OR a reviewer co-signed exception.

calls internal: _nonempty x2, DiagnosisError, _exception_cosigned
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

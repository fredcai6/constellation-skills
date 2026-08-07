# scripts.verify_diagnosis:_exception_cosigned
function, scripts/verify_diagnosis.py:114, 7 lines

```python
def _exception_cosigned(finding: dict) -> bool
```

True only when an INDEPENDENT reviewer co-signed the exception AND a log

entry records it. Self-assertion (no reviewer_cosign) is not enough.

calls internal: _nonempty x2
calls stdlib: builtins.isinstance
reads stdlib: builtins.dict
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

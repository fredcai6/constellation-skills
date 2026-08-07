# scripts.verify_fowler_pass:_exception_cosigned
function, scripts/verify_fowler_pass.py:78, 7 lines

```python
def _exception_cosigned(record: dict) -> bool
```

True only when an INDEPENDENT reviewer co-signed a whole-pass skip AND a log

entry records it. Self-assertion (no reviewer_cosign) is not enough.

calls internal: _nonempty x2
calls stdlib: builtins.isinstance
reads stdlib: builtins.dict
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

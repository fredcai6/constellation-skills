# scripts.verify_interrogation:verify_finish_gate
function, scripts/verify_interrogation.py:129, 30 lines

```python
def verify_finish_gate(record: dict) -> None
```

The no-quit-early finish gate: a consolidated record needs the joint-

understanding sign-off AND no open question — or a reviewer-cosigned exception.

calls internal: _nonempty x2, InterrogationError, _exception_cosigned, _require
calls stdlib: builtins.isinstance
reads stdlib: builtins.dict
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

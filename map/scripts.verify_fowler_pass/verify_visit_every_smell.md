# scripts.verify_fowler_pass:verify_visit_every_smell
function, scripts/verify_fowler_pass.py:118, 15 lines

```python
def verify_visit_every_smell(record: dict) -> None
```

Visit-every-item: every baseline smell has a verdict — unless a reviewer-

cosigned exception covers skipping the whole pass.

calls internal: FowlerPassError, _exception_cosigned
calls stdlib: builtins.str
reads internal: REQUIRED_SMELLS
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

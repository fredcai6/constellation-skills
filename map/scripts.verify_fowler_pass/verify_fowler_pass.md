# scripts.verify_fowler_pass:verify_fowler_pass
function, scripts/verify_fowler_pass.py:170, 7 lines

```python
def verify_fowler_pass(record: object) -> None
```

Raise FowlerPassError on any failed rule; return None if the record clears

the rail. Order is deliberate: shape first, then visit-every-smell, then the
override-log rail.

calls internal: verify_overrides_logged, verify_structure, verify_visit_every_smell
writes internal: verify_fowler_pass.record

referenced by: 1 sites, this module only

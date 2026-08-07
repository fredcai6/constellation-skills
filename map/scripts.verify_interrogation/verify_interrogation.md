# scripts.verify_interrogation:verify_interrogation
function, scripts/verify_interrogation.py:161, 7 lines

```python
def verify_interrogation(record: object) -> None
```

Raise InterrogationError on any failed rule; return None if the record

clears the rail. Order is deliberate: shape first, then the split, then the
finish gate.

calls internal: verify_finish_gate, verify_split, verify_structure
writes internal: verify_interrogation.record

referenced by: 1 sites, this module only

# scripts.verify_diagnosis:verify_diagnosis
function, scripts/verify_diagnosis.py:164, 7 lines

```python
def verify_diagnosis(finding: object) -> None
```

Raise DiagnosisError on any failed rule; return None if the finding record

clears the rail. Order is deliberate: shape first, then the reproduce gate.

calls internal: verify_map_staleness_caveat, verify_reproduce_before_claim, verify_route, verify_structure
writes internal: verify_diagnosis.finding

referenced by: 1 sites, this module only

# tests.test_checklist_engine:_artifact_gate
function, tests/test_checklist_engine.py:202, 10 lines

```python
def _artifact_gate(iid, status='in-progress')
```

A gate whose single postcondition is an `artifact`/`review-result`

check matching `verdict: APPROVE` (the gN-review / gN-integrate shape).

calls internal: gate

referenced by: 18 sites, this module only

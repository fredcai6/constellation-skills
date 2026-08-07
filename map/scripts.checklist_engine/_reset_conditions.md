# scripts.checklist_engine:_reset_conditions
function, scripts/checklist_engine.py:1919, 10 lines

```python
def _reset_conditions(conds: list[dict]) -> None
```

Reset each condition to unsatisfied and drop the markers that would let a

stale approval carry across a rework: `satisfied_by`, `waived` (a prior human
waiver does not survive rework) and `attested` (nor an artifact-by-reference
attestation). Shared by the target-gate reset and the downstream cascade.

unresolved: 3 calls (dispatch-unknown-base)

referenced by: 4 sites, this module only

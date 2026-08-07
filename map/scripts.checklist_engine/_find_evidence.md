# scripts.checklist_engine:_find_evidence
function, scripts/checklist_engine.py:463, 10 lines

```python
def _find_evidence(cl: dict, eid: str) -> dict | None
```

Find an evidence item by id across ALL tasks' evidence lists. Evidence ids

are globally unique (`e-<task>-<n>`), so a checklist-wide search lets one task's
artifact postcondition be satisfied by reference to an artifact attached to a
sibling task (see `attest --evidence`). Returns the evidence dict or None.

unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

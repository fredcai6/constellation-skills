# scripts.checklist_engine:_supersede_evidence
function, scripts/checklist_engine.py:1931, 7 lines

```python
def _supersede_evidence(t: dict, iid: str, reason: str) -> None
```

Mark every evidence item on task `t` superseded by a reopen of `iid`.

Evidence is RETAINED (audit trail preserved) but rendered inert for
satisfaction (see `_check_condition` artifact branch and `attest --evidence`):
a reopened gate must not re-pass from the stale approval it just invalidated.

calls internal: _now
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

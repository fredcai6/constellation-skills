# scripts.verify_diagnosis:verify_route
function, scripts/verify_diagnosis.py:141, 21 lines

```python
def verify_route(finding: dict) -> None
```

Rule 4: route out (don't fix). A confirmed fault goes to triage/reviewer;

an explained-by-design finding is handed back as a note.

calls internal: _require x3
reads internal: VALID_ROUTES x2
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

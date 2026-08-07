# scripts.run_crew:session_name
function, scripts/run_crew.py:83, 6 lines

```python
def session_name(work_id: str, gate: str, role: str, attempt: int) -> str
```

Deterministic, stable crew session name.

`constellation/<work-id>/<gate>/<role>/attempt-<n>` — the same inputs always
produce the same name, so a recovery can address an attempt unambiguously.

referenced by: 1 sites, this module only

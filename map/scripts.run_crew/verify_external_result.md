# scripts.run_crew:verify_external_result
function, scripts/run_crew.py:744, 6 lines

```python
def verify_external_result(entries: list[dict], session: str, root: Path) -> tuple[bool, dict]
```

Verify whether the result artifact is present AND fresh for a recorded

attempt and, when fresh, mark it resolved/`completed`. Thin wrapper over the
backend-uniform `CrewBackend.verify` (signature + observable behavior
preserved). Returns (fresh, entry). Reuses the canonical `result_fresh`.

calls internal: ExternalBackend
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

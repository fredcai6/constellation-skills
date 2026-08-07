# scripts.checklist_engine:_append_why
function, scripts/checklist_engine.py:1056, 12 lines

```python
def _append_why(cl: dict, gate: str, why: str | None, mechanical: bool) -> str
```

Append one why-record to the top-level append-only `why_trail` and return

its id. `why` is the running-understanding text (None for a mechanical step).
`setdefault` creates `why_trail` on first write so legacy spines drive
unchanged. Never mutates or removes a prior entry.

calls internal: _now
calls stdlib: builtins.bool, builtins.len
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

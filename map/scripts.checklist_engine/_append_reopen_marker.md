# scripts.checklist_engine:_append_reopen_marker
function, scripts/checklist_engine.py:1070, 10 lines

```python
def _append_reopen_marker(cl: dict, gate: str, reason: str) -> None
```

Append a reopen-marker to `why_trail`: the append-only way a `reopen`

FRESHENS the digest. A why-record for `gate` is stale once a later reopen-marker
names that gate, so `_latest_why_record` skips past it — no prior row edited.

calls internal: _now
calls stdlib: builtins.len
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

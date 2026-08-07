# scripts.checklist_engine:append_journal_entry
function, scripts/checklist_engine.py:2655, 23 lines

```python
def append_journal_entry(spine_path: Path, verb: str, task_id: str | None, session_id: str | None, evidence_ids: list[str]) -> None
```

Append one hash-chained line to the spine's journal for a successful

mutating verb. Best-effort and non-fatal: a journal write failure must never
fail the mutation it records (the spine is already the source of truth), so any
OSError is swallowed.

calls internal: _journal_hash, _now, _read_journal_tail, journal_path
calls stdlib: builtins.sorted, json.dumps
reads stdlib: builtins.OSError, json (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

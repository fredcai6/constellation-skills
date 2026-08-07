# scripts.checklist_engine:_read_journal_tail
function, scripts/checklist_engine.py:2638, 15 lines

```python
def _read_journal_tail(jp: Path) -> tuple[int, str]
```

(next seq, last hash) for an existing journal, or (1, "") when absent/empty.

Never raises — a corrupt/unreadable journal degrades to a fresh chain rather
than blocking the engine (the sidecar must never break a mutation).

calls stdlib: builtins.len x2, json.loads
reads stdlib: builtins.OSError, builtins.ValueError, json (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

# evals.euler-2-even-fibonacci.checks.spine_completed:_journal_hash
function, evals/euler-2-even-fibonacci/checks/spine_completed.py:213, 7 lines

```python
def _journal_hash(entry: dict) -> str
```

Re-derive an entry's hash exactly as checklist_engine._journal_hash does:

SHA-256 over the canonical (sorted, hash-excluded) JSON of the fixed field set.

calls stdlib: hashlib.sha256, json.dumps
reads internal: JOURNAL_HASH_FIELDS
reads stdlib: hashlib (module), json (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

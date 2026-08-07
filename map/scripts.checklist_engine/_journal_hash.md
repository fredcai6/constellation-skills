# scripts.checklist_engine:_journal_hash
function, scripts/checklist_engine.py:2627, 9 lines

```python
def _journal_hash(entry: dict) -> str
```

SHA-256 over the entry's canonical (sorted, hash-excluded) JSON. The

``prev_hash`` field is part of that payload, so each line commits to the whole
chain before it — tampering with any earlier line invalidates every hash after.

calls stdlib: hashlib.sha256, json.dumps
reads stdlib: hashlib (module), json (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

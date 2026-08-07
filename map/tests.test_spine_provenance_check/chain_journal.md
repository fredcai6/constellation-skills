# tests.test_spine_provenance_check:chain_journal
function, tests/test_spine_provenance_check.py:273, 10 lines

```python
def chain_journal(rows, session_id='cmd-pe1') -> str
```

Build a valid hash-chained journal from (ts, verb, task, evidence_ids) rows.

calls internal: _jhash
calls stdlib: builtins.enumerate, json.dumps
reads stdlib: json (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 9 sites, this module only

# tests.test_spine_provenance_check:test_journal_tampered_hash_fails
function, tests/test_spine_provenance_check.py:329, 8 lines

```python
def test_journal_tampered_hash_fails(tmp_path)
```

HOLE: no docstring

calls internal: genuine_spine x2, chain_journal, genuine_rows, write_spine_and_journal
calls stdlib: json.dumps, json.loads
reads internal: chk
reads stdlib: json (module) x2
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found

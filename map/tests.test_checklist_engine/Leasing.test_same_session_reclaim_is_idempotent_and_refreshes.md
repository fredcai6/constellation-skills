# tests.test_checklist_engine:Leasing.test_same_session_reclaim_is_idempotent_and_refreshes
method, tests/test_checklist_engine.py:648, 9 lines

```python
def test_same_session_reclaim_is_idempotent_and_refreshes(self)
```

HOLE: no docstring

calls internal: Leasing.assertEqual, Leasing.assertIn, Leasing.assertNotEqual, _old_ts, gate, gated
reads internal: E x2, PASS_COMMAND
unresolved: 2 calls (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: none found

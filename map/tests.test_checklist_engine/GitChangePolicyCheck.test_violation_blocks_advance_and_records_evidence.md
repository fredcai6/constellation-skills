# tests.test_checklist_engine:GitChangePolicyCheck.test_violation_blocks_advance_and_records_evidence
method, tests/test_checklist_engine.py:1001, 10 lines

```python
def test_violation_blocks_advance_and_records_evidence(self)
```

HOLE: no docstring

calls internal: GitChangePolicyCheck.assertEqual x2, GitChangePolicyCheck._gate, GitChangePolicyCheck.assertIn, GitChangePolicyCheck.assertRaises, GitChangePolicyCheck.assertTrue
reads internal: E x2
writes internal: GitChangePolicyCheck._files
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

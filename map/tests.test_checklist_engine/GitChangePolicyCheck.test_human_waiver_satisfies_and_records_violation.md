# tests.test_checklist_engine:GitChangePolicyCheck.test_human_waiver_satisfies_and_records_violation
method, tests/test_checklist_engine.py:1024, 22 lines

```python
def test_human_waiver_satisfies_and_records_violation(self)
```

HOLE: no docstring

calls internal: GitChangePolicyCheck.assertEqual x4, GitChangePolicyCheck.assertIn x3, GitChangePolicyCheck._gate, GitChangePolicyCheck.assertRaises, GitChangePolicyCheck.assertTrue
calls stdlib: builtins.next
reads internal: E x4
writes internal: GitChangePolicyCheck._files
unresolved: 3 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

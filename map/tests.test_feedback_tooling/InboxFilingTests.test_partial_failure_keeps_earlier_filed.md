# tests.test_feedback_tooling:InboxFilingTests.test_partial_failure_keeps_earlier_filed
method, tests/test_feedback_tooling.py:459, 16 lines

```python
def test_partial_failure_keeps_earlier_filed(self)
```

HOLE: no docstring

- [flaky](InboxFilingTests.test_partial_failure_keeps_earlier_filed.flaky.md) method: HOLE: no docstring

calls internal: InboxFilingTests._merged, InboxFilingTests.assertEqual, InboxFilingTests.assertRaises
calls stdlib: builtins.len, json.loads
reads internal: InboxFilingTests.inbox x2, InboxFilingTests.m
reads stdlib: builtins.RuntimeError, json (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found

# tests.test_feedback_tooling:InboxFilingTests.test_idempotent_no_double_file
method, tests/test_feedback_tooling.py:419, 8 lines

```python
def test_idempotent_no_double_file(self)
```

HOLE: no docstring

calls internal: InboxFilingTests._merged x2, InboxFilingTests.assertEqual x2, InboxFilingTests._fake_filer
calls stdlib: builtins.len
reads internal: InboxFilingTests.inbox x2, InboxFilingTests.m x2
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

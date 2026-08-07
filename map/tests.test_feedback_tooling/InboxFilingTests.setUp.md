# tests.test_feedback_tooling:InboxFilingTests.setUp
method, tests/test_feedback_tooling.py:350, 20 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: InboxFilingTests._write_project x2, load
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: FEEDBACK_ENTRY, InboxFilingTests.base, InboxFilingTests.tmp
reads stdlib: tempfile (module)
writes internal: InboxFilingTests.base, InboxFilingTests.inbox, InboxFilingTests.m, InboxFilingTests.roots, InboxFilingTests.tmp
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

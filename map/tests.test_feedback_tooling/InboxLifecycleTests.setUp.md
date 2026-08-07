# tests.test_feedback_tooling:InboxLifecycleTests.setUp
method, tests/test_feedback_tooling.py:502, 8 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: InboxLifecycleTests._project, load
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: FEEDBACK_ENTRY, InboxLifecycleTests.base, InboxLifecycleTests.tmp
reads stdlib: tempfile (module)
writes internal: InboxLifecycleTests.base, InboxLifecycleTests.inbox, InboxLifecycleTests.m, InboxLifecycleTests.roots, InboxLifecycleTests.tmp
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

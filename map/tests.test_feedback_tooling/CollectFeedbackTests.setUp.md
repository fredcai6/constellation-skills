# tests.test_feedback_tooling:CollectFeedbackTests.setUp
method, tests/test_feedback_tooling.py:104, 11 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: load
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: CollectFeedbackTests.roots, CollectFeedbackTests.tmp, FEEDBACK_ENTRY
reads stdlib: tempfile (module)
writes internal: CollectFeedbackTests.m, CollectFeedbackTests.roots, CollectFeedbackTests.tmp
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

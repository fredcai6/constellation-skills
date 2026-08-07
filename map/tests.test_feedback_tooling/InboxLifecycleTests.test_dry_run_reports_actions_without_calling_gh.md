# tests.test_feedback_tooling:InboxLifecycleTests.test_dry_run_reports_actions_without_calling_gh
method, tests/test_feedback_tooling.py:568, 11 lines

```python
def test_dry_run_reports_actions_without_calling_gh(self)
```

HOLE: no docstring

calls internal: InboxLifecycleTests.assertEqual x3, InboxLifecycleTests._file_once, InboxLifecycleTests._filer, InboxLifecycleTests._merged, InboxLifecycleTests._project, InboxLifecycleTests._recorder
calls stdlib: builtins.len x2
reads internal: FEEDBACK_ENTRY, InboxLifecycleTests.inbox, InboxLifecycleTests.m
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

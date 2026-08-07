# tests.test_agent_work_root:DurableRootEpicLeaseTests.test_verify_agent_feedback_resolves_to_worktree_under_lease
method, tests/test_agent_work_root.py:153, 20 lines

```python
def test_verify_agent_feedback_resolves_to_worktree_under_lease(self)
```

HOLE: no docstring

calls internal: DurableRootEpicLeaseTests.assertEqual, _load, _write_lease
calls stdlib: os.chdir x2, os.getcwd
reads internal: DurableRootEpicLeaseTests.linked x2, DurableRootEpicLeaseTests.main
reads stdlib: os (module) x3
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

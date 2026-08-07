# tests.test_agent_work_root:DurableRootEpicLeaseTests
class, tests/test_agent_work_root.py:105, 68 lines

```python
@unittest.skipUnless(GIT, 'git not available on PATH')
class DurableRootEpicLeaseTests(TestCase)
```

Under an ACTIVE Admiral epic lease in the main checkout, `durable_root`

honors the linked worktree (its normal fallback) instead of redirecting to the
fenced main checkout. Any other lease state leaves the redirect unchanged, and
the lease scan never raises.

- [setUp](DurableRootEpicLeaseTests.setUp.md) method: HOLE: no docstring
- [tearDown](DurableRootEpicLeaseTests.tearDown.md) method: HOLE: no docstring
- [test_active_admiral_lease_resolves_to_worktree](DurableRootEpicLeaseTests.test_active_admiral_lease_resolves_to_worktree.md) method: HOLE: no docstring
- [test_active_explorer_lease_resolves_to_main](DurableRootEpicLeaseTests.test_active_explorer_lease_resolves_to_main.md) method: HOLE: no docstring
- [test_released_admiral_lease_resolves_to_main](DurableRootEpicLeaseTests.test_released_admiral_lease_resolves_to_main.md) method: HOLE: no docstring
- [test_no_lease_resolves_to_main](DurableRootEpicLeaseTests.test_no_lease_resolves_to_main.md) method: HOLE: no docstring
- [test_malformed_spine_does_not_raise_and_resolves_to_main](DurableRootEpicLeaseTests.test_malformed_spine_does_not_raise_and_resolves_to_main.md) method: HOLE: no docstring
- [test_verify_agent_feedback_resolves_to_worktree_under_lease](DurableRootEpicLeaseTests.test_verify_agent_feedback_resolves_to_worktree_under_lease.md) method: HOLE: no docstring

referenced by: none found

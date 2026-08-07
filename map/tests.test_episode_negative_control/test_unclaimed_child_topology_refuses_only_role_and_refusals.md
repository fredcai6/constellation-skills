# tests.test_episode_negative_control:test_unclaimed_child_topology_refuses_only_role_and_refusals
function, tests/test_episode_negative_control.py:755, 15 lines

```python
def test_unclaimed_child_topology_refuses_only_role_and_refusals(control)
```

(b) The PRODUCTION shape: gates live in a child gate-plan that never gets a

lease, so `role` and `refusals` are structurally unavailable — and the other eight
fields are still present and correct.

calls internal: compare_fields
calls stdlib: builtins.sorted
reads third-party: episode_capture (module), episode_capture.REQUIRED_MECHANICAL_FIELDS
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

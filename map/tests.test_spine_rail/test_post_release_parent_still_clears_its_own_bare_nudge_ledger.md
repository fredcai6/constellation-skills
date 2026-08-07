# tests.test_spine_rail:test_post_release_parent_still_clears_its_own_bare_nudge_ledger
function, tests/test_spine_rail.py:378, 10 lines

```python
def test_post_release_parent_still_clears_its_own_bare_nudge_ledger(proj)
```

The other half of the same rule: a top-level release still clears the

bare-keyed ledger, so the pre-#419 behavior is intact.

calls internal: _real_post_tool_use x2, _claim_cmd, _real_parent_payloads, _release_cmd
reads internal: sr x4
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found

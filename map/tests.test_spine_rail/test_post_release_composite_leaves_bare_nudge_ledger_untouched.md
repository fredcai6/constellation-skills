# tests.test_spine_rail:test_post_release_composite_leaves_bare_nudge_ledger_untouched
function, tests/test_spine_rail.py:364, 12 lines

```python
def test_post_release_composite_leaves_bare_nudge_ledger_untouched(proj)
```

The nudge / three-strike escape-hatch ledger stays keyed by the BARE

session_id, so a subagent's release must not clear the parent's strikes.

calls internal: _real_post_tool_use x2, _claim_cmd, _real_subagent_payloads, _release_cmd
reads internal: sr x4
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found

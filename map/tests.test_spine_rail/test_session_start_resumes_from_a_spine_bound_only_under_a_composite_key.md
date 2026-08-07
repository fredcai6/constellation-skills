# tests.test_spine_rail:test_session_start_resumes_from_a_spine_bound_only_under_a_composite_key
function, tests/test_spine_rail.py:513, 19 lines

```python
def test_session_start_resumes_from_a_spine_bound_only_under_a_composite_key(proj)
```

decide_session_start's read goes through session_view too. The spine

lives outside proj/.agent-work so the fallback scan cannot find it -- the
only route to it is the composite key.

calls internal: _claim_cmd, _real_post_tool_use, _real_subagent_payloads, make_spine, write_spine
calls stdlib: builtins.list, builtins.str
reads internal: sr x5
unresolved: 5 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

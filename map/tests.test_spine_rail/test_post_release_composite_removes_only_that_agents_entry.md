# tests.test_spine_rail:test_post_release_composite_removes_only_that_agents_entry
function, tests/test_spine_rail.py:341, 21 lines

```python
def test_post_release_composite_removes_only_that_agents_entry(proj)
```

A release carrying agent_id removes only that agent's entry: the other

agent's key set and the parent's bare key set both survive.

calls internal: _real_post_tool_use x4, _claim_cmd x3, _abs_spine x2, _real_parent_payloads, _real_subagent_payloads, _release_cmd
calls stdlib: builtins.list x2, builtins.len, builtins.set
reads internal: sr x8
unresolved: 9 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

# tests.test_spine_rail:test_post_claim_two_agent_ids_give_two_independent_key_sets
function, tests/test_spine_rail.py:320, 19 lines

```python
def test_post_claim_two_agent_ids_give_two_independent_key_sets(proj)
```

Two distinct agent_ids on ONE session_id produce two independent key

sets -- exactly the case that used to collapse into one ambiguous key.

calls internal: _abs_spine x2, _claim_cmd x2, _real_post_tool_use x2, _real_subagent_payloads
calls stdlib: builtins.list x2, builtins.len, builtins.set
reads internal: sr x5
unresolved: 7 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

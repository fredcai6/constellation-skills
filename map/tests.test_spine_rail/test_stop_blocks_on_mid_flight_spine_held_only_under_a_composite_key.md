# tests.test_spine_rail:test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key
function, tests/test_spine_rail.py:486, 25 lines

```python
def test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key(proj)
```

The parent's bare key holds nothing mid-flight; the only mid-flight

spine is bound under a SUBAGENT's composite key. Before the read routing
this Stop was allowed (the bare key looked idle), which is exactly the
silence being fixed.

calls internal: _claim_cmd x2, _real_post_tool_use x2, make_spine x2, write_spine x2, _abs_spine, _real_parent_payloads, _real_subagent_payloads
calls stdlib: builtins.list x2, builtins.len, builtins.str
reads internal: sr x5
unresolved: 7 calls (dispatch-unknown-base)

referenced by: none found

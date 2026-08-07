# tests.test_spine_rail:test_post_claim_unusable_agent_id_writes_no_binding_anywhere
function, tests/test_spine_rail.py:390, 20 lines

```python
def test_post_claim_unusable_agent_id_writes_no_binding_anywhere(proj)
```

An unresolved identity binds NOTHING -- not under a composite key, and

above all not under the parent's bare key, which is where a two-way
fallback would have silenced the parent's gauge.

calls internal: _abs_spine x2, _claim_cmd x2, _real_post_tool_use x2, _derive, _real_parent_payloads, _real_subagent_payloads
calls stdlib: json.dumps x2, builtins.list, builtins.set
reads internal: sr x4
reads stdlib: json (module) x2
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found

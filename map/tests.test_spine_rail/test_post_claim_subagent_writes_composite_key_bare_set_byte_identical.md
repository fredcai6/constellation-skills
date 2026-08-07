# tests.test_spine_rail:test_post_claim_subagent_writes_composite_key_bare_set_byte_identical
function, tests/test_spine_rail.py:296, 22 lines

```python
def test_post_claim_subagent_writes_composite_key_bare_set_byte_identical(proj)
```

A claim carrying agent_id files under sid#agent_id and leaves the bare

sid entry set byte-identical -- the parent's gauge candidate count is
unchanged, which is the whole point of the re-key.

calls internal: _abs_spine x3, _claim_cmd x2, _real_post_tool_use x2, _real_parent_payloads, _real_subagent_payloads
calls stdlib: builtins.list x2, json.dumps x2, builtins.set
reads internal: sr x5
reads stdlib: json (module) x2
unresolved: 7 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

# tests.test_spine_rail:test_session_view_merges_one_bare_and_two_composite_keys
function, tests/test_spine_rail.py:439, 45 lines

```python
def test_session_view_merges_one_bare_and_two_composite_keys(proj)
```

The settle a cold critic flagged as otherwise vacuous: on a store with

ONLY bare keys the merge is the identity function, so it would pass in
exactly the world where session_view ignores composite keys. This store
holds one bare key and TWO composite keys, written by the real claim
writer from real payloads, plus two decoy keys that must NOT be merged.

calls internal: _abs_spine x3, _claim_cmd x3, _real_post_tool_use x3, _real_parent_payloads, _real_subagent_payloads
calls stdlib: builtins.len x3, builtins.dict x2, builtins.set x2, builtins.print
reads internal: sr x12
unresolved: 12 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

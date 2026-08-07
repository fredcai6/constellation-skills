# tests.test_spine_rail:test_post_claim_same_spine_reclaim_overwrites_only_itself
function, tests/test_spine_rail.py:1208, 22 lines

```python
def test_post_claim_same_spine_reclaim_overwrites_only_itself(proj)
```

A THIRD claim for the SAME spine (same session_id, same abs_spine)

overwrites only that one entry -- the sibling entry for the other spine
survives untouched.

calls internal: _bash x3
calls stdlib: builtins.str x5, builtins.len
reads internal: sr x5
unresolved: 7 calls (dispatch-unknown-base)

referenced by: none found

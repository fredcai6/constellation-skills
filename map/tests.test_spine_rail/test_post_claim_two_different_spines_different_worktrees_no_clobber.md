# tests.test_spine_rail:test_post_claim_two_different_spines_different_worktrees_no_clobber
function, tests/test_spine_rail.py:1185, 21 lines

```python
def test_post_claim_two_different_spines_different_worktrees_no_clobber(proj)
```

Same session_id, two DIFFERENT spines resolved from two DIFFERENT

worktrees -- both persist as distinct entries. This is the case a
'worktree' key (even a correctly-derived one) would ALSO collide if both
spines happened to share a worktree; here they don't even share one, so
it is doubly clear the key must be the spine path itself, not the
worktree.

calls internal: _bash x2
calls stdlib: builtins.str x6, builtins.len, builtins.set
reads internal: sr x3
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found

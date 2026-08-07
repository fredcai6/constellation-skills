# tests.test_spine_rail:test_post_claim_two_different_spines_same_worktree_no_clobber
function, tests/test_spine_rail.py:1165, 18 lines

```python
def test_post_claim_two_different_spines_same_worktree_no_clobber(proj)
```

Two claims under the SAME session_id, for two DIFFERENT spines, both

resolved from the SAME worktree (cwd) -- both must persist as distinct
entries; neither clobbers the other (decision:key-binding-by-spine-path-
not-worktree-or-cwd -- keying by worktree alone would have collided these
two).

calls internal: _bash x2
calls stdlib: builtins.str x4, builtins.len, builtins.set
reads internal: sr x3
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found

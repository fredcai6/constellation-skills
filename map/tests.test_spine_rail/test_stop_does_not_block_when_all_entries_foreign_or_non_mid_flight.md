# tests.test_spine_rail:test_stop_does_not_block_when_all_entries_foreign_or_non_mid_flight
function, tests/test_spine_rail.py:783, 15 lines

```python
def test_stop_does_not_block_when_all_entries_foreign_or_non_mid_flight(proj)
```

One session_id bound to TWO spines: one is genuinely mid-flight but

FOREIGN (a subagent's own worktree, parent stopping elsewhere), the other
is not mid-flight at all (released lease). Neither should block -- the
Stop is allowed.

calls internal: bind x2, make_spine x2, write_spine x2
calls stdlib: builtins.str x2, builtins.len
reads internal: sr x3
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

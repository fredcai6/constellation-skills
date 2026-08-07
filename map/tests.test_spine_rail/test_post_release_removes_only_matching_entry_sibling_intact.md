# tests.test_spine_rail:test_post_release_removes_only_matching_entry_sibling_intact
function, tests/test_spine_rail.py:1232, 15 lines

```python
def test_post_release_removes_only_matching_entry_sibling_intact(proj)
```

release removes ONLY the entry for the released spine, leaving a

sibling entry for a different spine under the same session_id intact.

calls internal: _bash x3
calls stdlib: builtins.str x4, builtins.set
reads internal: sr x4
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found

# tests.test_spine_rail:test_session_start_unambiguous_scan_merges_onto_existing_sibling_binding
function, tests/test_spine_rail.py:984, 24 lines

```python
def test_session_start_unambiguous_scan_merges_onto_existing_sibling_binding(proj)
```

The bind-on-unambiguous-scan write must not clobber a sibling

abs_spine_path entry this sid already holds for a DIFFERENT (foreign-
worktree) spine (mirrors the real claim writer's leave-siblings-
untouched behavior, #202). The sibling is made FOREIGN on purpose: a
non-foreign sibling would already satisfy the existing-binding read
(g1's territory, unrelated to this scan-bind path) and the scan would
never run at all -- foreign is the one shape that reaches this branch
with a pre-existing sibling still in place.

calls internal: make_spine x2, write_spine x2, bind
calls stdlib: builtins.str x2, builtins.set
reads internal: sr x2
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

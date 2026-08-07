# tests.test_spine_rail:test_session_start_zero_matches_writes_no_binding
function, tests/test_spine_rail.py:908, 7 lines

```python
def test_session_start_zero_matches_writes_no_binding(proj)
```

No .agent-work/*/spine.json at all -> the existing zero-match

behavior (empty {} response) is unchanged, AND no binding file is
created/written as a side effect of the scan finding nothing.

calls stdlib: builtins.str
reads internal: sr x3
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found

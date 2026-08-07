# tests.test_spine_rail:test_post_release_last_entry_removes_sid_key_entirely
function, tests/test_spine_rail.py:1249, 10 lines

```python
def test_post_release_last_entry_removes_sid_key_entirely(proj)
```

Releasing the only bound spine for a session_id removes the sid key

entirely (tidy, cosmetic -- not load-bearing).

calls internal: _bash x2
calls stdlib: builtins.str x2
reads internal: sr x4
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found

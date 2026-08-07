# tests.test_spine_rail:test_stop_blocks_when_any_of_two_entries_is_mid_flight
function, tests/test_spine_rail.py:767, 14 lines

```python
def test_stop_blocks_when_any_of_two_entries_is_mid_flight(proj)
```

One session_id bound to TWO spines: one already complete+released

(not mid-flight), the other genuinely in-progress with an active lease.
ANY non-foreign mid-flight entry must block the Stop.

calls internal: bind x2, make_spine x2, write_spine x2
calls stdlib: builtins.len
reads internal: sr x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found

# tests.test_spine_rail:test_session_start_no_bind_when_sid_missing
function, tests/test_spine_rail.py:970, 12 lines

```python
def test_session_start_no_bind_when_sid_missing(proj)
```

An unambiguous scan (exactly one active-leased spine) but no

session_id on the payload at all -- there is nothing to key a binding
by, so no write happens (fail-open: still injects context).

calls internal: make_spine, write_spine
calls stdlib: builtins.str
reads internal: sr x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found

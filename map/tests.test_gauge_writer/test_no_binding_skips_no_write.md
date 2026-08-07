# tests.test_gauge_writer:test_no_binding_skips_no_write
function, tests/test_gauge_writer.py:190, 6 lines

```python
def test_no_binding_skips_no_write(proj)
```

No session->spine binding (e.g. no engine claim has run yet this

session) -- work_id is unresolvable, so the hook must skip entirely.

calls internal: _hook_data
calls stdlib: builtins.list
reads internal: _FIXTURE, gw
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

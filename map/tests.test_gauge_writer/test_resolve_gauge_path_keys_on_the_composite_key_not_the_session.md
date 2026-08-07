# tests.test_gauge_writer:test_resolve_gauge_path_keys_on_the_composite_key_not_the_session
function, tests/test_gauge_writer.py:738, 13 lines

```python
def test_resolve_gauge_path_keys_on_the_composite_key_not_the_session(proj)
```

A parent and its dispatched agent share a session_id but hold DISTINCT

bindings. Each key must see exactly its own -- one candidate each, so
neither is ambiguous and neither goes silent.

calls internal: _bind x2
reads internal: gw x2
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found

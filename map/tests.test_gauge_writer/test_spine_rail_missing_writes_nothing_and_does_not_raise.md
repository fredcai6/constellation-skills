# tests.test_gauge_writer:test_spine_rail_missing_writes_nothing_and_does_not_raise
function, tests/test_gauge_writer.py:791, 11 lines

```python
def test_spine_rail_missing_writes_nothing_and_does_not_raise(proj, monkeypatch)
```

End-to-end companion to the guard unit test above: with the sibling

module unloadable, the handler skips deliberately rather than by way of an
exception, and still returns the neutral payload.

calls internal: _agent_hook_data, _bound_work, _hook_data
reads internal: gw x4, _FIXTURE x2
unresolved: 5 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

# tests.test_gauge_writer:test_unresolvable_identity_writes_nothing
function, tests/test_gauge_writer.py:773, 16 lines

```python
def test_unresolvable_identity_writes_nothing(proj)
```

The issue's own named negative control. An agent_id the key composer

cannot use (empty, non-string, or carrying the separator) must NOT fall
back to the bare session_id -- that files the SUBAGENT's reading under the
PARENT's key, which is the same misattribution wearing a different hat.

calls internal: _agent_hook_data, _bind
calls stdlib: builtins.list x3
reads internal: gw x3, _FIXTURE
unresolved: 6 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

# tests.test_gauge_writer:test_subagent_payload_never_writes_to_the_parents_gauge
function, tests/test_gauge_writer.py:753, 18 lines

```python
def test_subagent_payload_never_writes_to_the_parents_gauge(proj)
```

THE misattribution this gate exists to prevent. The parent holds the

bare-session binding; a dispatched agent's tool call carries the parent's
transcript_path. Resolving by session_id alone would write the PARENT's
reading -- from the PARENT's transcript -- as if it were this agent's.

The subagent's own key is unbound here, so the correct outcome is zero
candidates: write nothing, anywhere.

calls internal: _agent_hook_data, _bind
calls stdlib: builtins.list x3
reads internal: gw x3, _FIXTURE
unresolved: 6 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

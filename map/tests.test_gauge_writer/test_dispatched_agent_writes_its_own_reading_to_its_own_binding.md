# tests.test_gauge_writer:test_dispatched_agent_writes_its_own_reading_to_its_own_binding
function, tests/test_gauge_writer.py:1128, 24 lines

```python
def test_dispatched_agent_writes_its_own_reading_to_its_own_binding(proj)
```

End to end, the whole point of the gate: a dispatched agent and its

parent share one session_id but hold distinct bindings; the agent's
reading is computed from ITS OWN transcript and lands in ITS OWN work
dir, and the parent's gauge is not touched at all.

calls internal: _agent_hook_data, _bind, _bound_subagent_work, _parent_transcript, _plant_derived_transcript
calls stdlib: json.loads
calls third-party: pytest.approx
reads internal: _PARENT_AGENT_ID x3, gw x2, _REAL_SUBAGENT_OBSERVED_AT, _REAL_SUBAGENT_TOKENS
reads stdlib: json (module)
reads third-party: pytest (module)
unresolved: 6 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

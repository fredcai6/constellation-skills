# tests.test_gauge_writer:_agent_hook_data
function, tests/test_gauge_writer.py:701, 11 lines

```python
def _agent_hook_data(session_id='s1', agent_id='a1', transcript_path=None)
```

A payload as the harness delivers it for a DISPATCHED agent: the

parent's transcript_path plus the acting agent's own agent_id.

Constructing this by hand is legitimate at this level -- the ban on
supplying agent_id binds the LIVE acceptance run (gate g4), whose whole
point is proving the harness delivers it. Here we test rejection and
attribution, not delivery.

calls internal: _hook_data

referenced by: 11 sites, this module only

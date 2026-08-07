# tests.test_spine_rail:probe_payloads
function, tests/test_spine_rail.py:121, 6 lines

```python
def probe_payloads()
```

The real hook payloads, UNWRAPPED out of the capture wrapper's `payload`

key. Every test built on the capture goes through here: the wrapper is the
probe's own envelope and carries no `agent_id` at its top level, so reading
a wrapper as if it were a payload would test nothing that ships.

calls internal: _probe_wrappers

referenced by: 6 sites, this module only

# tests.test_spine_rail:test_binding_key_rejects_unusable_agent_ids_derived_from_real_payloads
function, tests/test_spine_rail.py:222, 29 lines

```python
def test_binding_key_rejects_unusable_agent_ids_derived_from_real_payloads()
```

Fail closed. Every row below is a real captured payload with ONE field

mutated; each must bind NOTHING rather than fall back to the bare key.

calls internal: _derive x12, probe_payloads x2
calls stdlib: builtins.len x2, builtins.print x2
reads internal: sr x3, _ABSENT x2
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found

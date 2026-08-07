# tests.test_gauge_writer:test_rejected_agent_id_writes_nothing_even_when_its_key_is_bound
function, tests/test_gauge_writer.py:829, 16 lines

```python
def test_rejected_agent_id_writes_nothing_even_when_its_key_is_bound(proj)
```

A rejected value means WRITE NOTHING -- never a repaired or sanitized

path. Adversarial setup: the offending composite key IS bound, so an
implementation that admitted the character would have somewhere to write
and would write there.

calls internal: _agent_hook_data, _bind
calls stdlib: builtins.list x3
reads internal: gw x3, _FIXTURE
unresolved: 6 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

# tests.test_gauge_writer:test_identity_resolution_duration_is_recorded_within_budget
function, tests/test_gauge_writer.py:1201, 10 lines

```python
def test_identity_resolution_duration_is_recorded_within_budget(proj)
```

Identity is an O(1) payload lookup plus a derived path, so the 100ms

placeholder budget should never be in danger -- but 'should' is not
evidence, so the writer records what it actually cost.

calls internal: _write_a_subagent_reading
calls stdlib: builtins.isinstance, builtins.set
reads internal: _IDENTITY_BUDGET_MS
reads stdlib: builtins.float
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

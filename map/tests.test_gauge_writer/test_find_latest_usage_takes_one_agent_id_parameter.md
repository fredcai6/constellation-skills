# tests.test_gauge_writer:test_find_latest_usage_takes_one_agent_id_parameter
function, tests/test_gauge_writer.py:1059, 9 lines

```python
def test_find_latest_usage_takes_one_agent_id_parameter(proj)
```

One parameter, not two. 'This is agent X's own transcript' is a single

fact; an expect_sidechain + expect_agent_id pair would let a caller set an
incoherent combination, and the agentId equality is what makes a wrong
derived path fail closed instead of producing a confidently misattributed
number.

calls stdlib: builtins.list x2, inspect.signature x2
reads internal: gw x2
reads stdlib: inspect (module) x2
unresolved: 4 reads (dispatch-unknown-base)

referenced by: none found

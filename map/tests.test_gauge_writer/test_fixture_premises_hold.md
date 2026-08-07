# tests.test_gauge_writer:test_fixture_premises_hold
function, tests/test_gauge_writer.py:1040, 17 lines

```python
def test_fixture_premises_hold(proj)
```

Pin the premises the assertions below rest on, so a fixture edit

breaks here rather than silently hollowing out the conjunct test.

calls stdlib: builtins.len x2, json.loads x2
reads internal: _PARENT_AGENT_ID x2, _MAINCHAIN_TAIL_FIXTURE, _REAL_SUBAGENT_FIXTURE
reads stdlib: json (module) x2
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found

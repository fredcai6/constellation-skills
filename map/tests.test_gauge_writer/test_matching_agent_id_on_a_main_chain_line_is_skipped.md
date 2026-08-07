# tests.test_gauge_writer:test_matching_agent_id_on_a_main_chain_line_is_skipped
function, tests/test_gauge_writer.py:1096, 10 lines

```python
def test_matching_agent_id_on_a_main_chain_line_is_skipped(proj, monkeypatch)
```

THE falsifier. The tail line carries the matching agentId, sits LAST so

the reverse scan meets it FIRST, and has a much bigger usage total on a
different model -- so an implementation checking agentId equality alone
returns it. The conjunct must skip it and keep going to the real sidechain
line. Reach: 2 of 5 lines (tail rejected, line 4 accepted).

calls internal: _reaching
reads internal: _MAINCHAIN_TAIL_FIXTURE, _PARENT_AGENT_ID, _REAL_SUBAGENT_OBSERVED_AT, _REAL_SUBAGENT_TOKENS, _TAIL_TOKENS

referenced by: none found

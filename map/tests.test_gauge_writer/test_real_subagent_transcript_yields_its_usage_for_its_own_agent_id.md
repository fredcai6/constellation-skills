# tests.test_gauge_writer:test_real_subagent_transcript_yields_its_usage_for_its_own_agent_id
function, tests/test_gauge_writer.py:1070, 7 lines

```python
def test_real_subagent_transcript_yields_its_usage_for_its_own_agent_id(proj, monkeypatch)
```

Given the fixture's OWN agentId the inverted filter returns the real

usage sum. Reach: 1 of 4 lines -- the answer is the last line, so the
scan hits it immediately.

calls internal: _reaching
reads internal: _PARENT_AGENT_ID, _REAL_SUBAGENT_FIXTURE, _REAL_SUBAGENT_OBSERVED_AT, _REAL_SUBAGENT_TOKENS

referenced by: none found

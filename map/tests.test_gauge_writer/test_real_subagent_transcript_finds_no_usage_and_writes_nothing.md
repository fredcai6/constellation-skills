# tests.test_gauge_writer:test_real_subagent_transcript_finds_no_usage_and_writes_nothing
function, tests/test_gauge_writer.py:421, 17 lines

```python
def test_real_subagent_transcript_finds_no_usage_and_writes_nothing(proj)
```

Adversarial confirmation of decision:gauge-write-fans-out-on-ambiguity's

residual open question: a REAL captured subagent transcript (every line
isSidechain: true, carrying the PARENT's own sessionId) must make
find_latest_usage skip every line and return None, so the PostToolUse
handler writes nothing -- even though the transcript DOES contain a
parseable assistant/usage record, just a sidechain one.

calls internal: _bind, _hook_data
reads internal: _REAL_SUBAGENT_FIXTURE x2, gw x2
unresolved: 5 calls (dispatch-unknown-base)

referenced by: none found

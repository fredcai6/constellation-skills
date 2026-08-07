# tests.test_gauge_writer:test_top_level_payload_still_reads_the_session_transcript
function, tests/test_gauge_writer.py:985, 11 lines

```python
def test_top_level_payload_still_reads_the_session_transcript(proj, monkeypatch)
```

The other half of the same invariant: with no agent_id, nothing is

derived and the session transcript is read exactly as today.

calls internal: _bound_work, _hook_data
calls stdlib: builtins.str x2
reads internal: gw x3, _FIXTURE x2
unresolved: 3 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base), 4 reads (unbound-name)

referenced by: none found

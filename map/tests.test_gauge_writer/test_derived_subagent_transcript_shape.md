# tests.test_gauge_writer:test_derived_subagent_transcript_shape
function, tests/test_gauge_writer.py:847, 11 lines

```python
def test_derived_subagent_transcript_shape(proj, tmp_path)
```

The acting agent's transcript is DERIVED from payload fields, never

searched for -- which is why the identical-command race a search would
have to worry about cannot arise here at all. Shape confirmed on disk for
both agents of a live two-subagent probe.

reads internal: _PARENT_AGENT_ID x2, gw
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

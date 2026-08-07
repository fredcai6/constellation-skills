# tests.test_gauge_writer:test_subagent_with_missing_derived_transcript_writes_no_gauge_at_all
function, tests/test_gauge_writer.py:941, 11 lines

```python
def test_subagent_with_missing_derived_transcript_writes_no_gauge_at_all(proj)
```

Same branch with no prior reading on disk -- the strongest form of

'unchanged' for a file that was never there. Only the sidecar appears.

calls internal: _agent_hook_data, _bound_subagent_work, _parent_transcript
calls stdlib: builtins.list x2, json.loads
reads internal: gw x3
reads stdlib: json (module)
unresolved: 4 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

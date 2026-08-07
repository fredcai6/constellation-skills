# tests.test_gauge_writer:test_subagent_with_missing_derived_transcript_leaves_gauge_untouched
function, tests/test_gauge_writer.py:905, 34 lines

```python
def test_subagent_with_missing_derived_transcript_leaves_gauge_untouched(proj)
```

THE fail-closed case. agent_id present, its own transcript absent: the

parent's transcript is RIGHT THERE and readable, and falling back to it is
exactly the misattribution #202/#261 already tried and reverted -- fan-out
did not fix ambiguity, it spread one agent's reading into an unrelated
agent's work area.

'Unchanged' is proved in BYTES and MTIME: the prior mtime is stamped to a
distinct past value first, so the assertion cannot pass by filesystem
timestamp granularity.

calls internal: _agent_hook_data, _bound_subagent_work, _parent_transcript
calls stdlib: builtins.isinstance, json.dumps, json.loads, os.utime
reads internal: gw x4
reads stdlib: json (module) x2, builtins.str, os (module)
unresolved: 9 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found

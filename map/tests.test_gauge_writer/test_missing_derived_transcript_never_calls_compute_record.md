# tests.test_gauge_writer:test_missing_derived_transcript_never_calls_compute_record
function, tests/test_gauge_writer.py:974, 9 lines

```python
def test_missing_derived_transcript_never_calls_compute_record(proj, monkeypatch)
```

The fail-closed branch returns BEFORE any reading is computed -- it

does not compute one and then decline to write it.

calls internal: _agent_hook_data, _bound_subagent_work, _parent_transcript
calls stdlib: builtins.str
reads internal: gw x2
unresolved: 3 calls (dispatch-unknown-base), 1 reads (unbound-name)

referenced by: none found

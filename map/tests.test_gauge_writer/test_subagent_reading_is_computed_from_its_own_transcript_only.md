# tests.test_gauge_writer:test_subagent_reading_is_computed_from_its_own_transcript_only
function, tests/test_gauge_writer.py:954, 18 lines

```python
def test_subagent_reading_is_computed_from_its_own_transcript_only(proj, monkeypatch)
```

There must be NO code path that hands the parent's transcript to

compute_record while agent_id is present. Asserted by intercepting
compute_record and recording exactly which path it was given.

calls internal: _agent_hook_data, _bound_subagent_work, _parent_transcript, _plant_derived_transcript
calls stdlib: builtins.str x3
reads internal: gw x3
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base), 4 reads (unbound-name)

referenced by: none found

# tests.test_gauge_writer:test_identity_resolution_duration_tracks_a_deliberately_slowed_step
function, tests/test_gauge_writer.py:1213, 15 lines

```python
def test_identity_resolution_duration_tracks_a_deliberately_slowed_step(proj, monkeypatch)
```

A constant would satisfy the assertion above. Slow the identity step by

a known amount and require the recorded value to follow it -- if the field
were hardcoded, or timed something else, this fails.

calls internal: _write_a_subagent_reading x2, _SlowRail
reads internal: gw x2, _IDENTITY_BUDGET_MS
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

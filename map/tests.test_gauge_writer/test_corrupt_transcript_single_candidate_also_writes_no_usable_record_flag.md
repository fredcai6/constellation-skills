# tests.test_gauge_writer:test_corrupt_transcript_single_candidate_also_writes_no_usable_record_flag
function, tests/test_gauge_writer.py:594, 11 lines

```python
def test_corrupt_transcript_single_candidate_also_writes_no_usable_record_flag(proj, tmp_path)
```

Unparseable transcript lines are also a compute_record (None, None)

outcome -- same 'no-usable-record' treatment as an empty transcript.

calls internal: _bound_work, _hook_data
calls stdlib: json.loads
reads internal: gw x2
reads stdlib: json (module)
unresolved: 3 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

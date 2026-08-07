# tests.test_gauge_writer:test_missing_transcript_path_never_writes_a_skip_flag
function, tests/test_gauge_writer.py:614, 7 lines

```python
def test_missing_transcript_path_never_writes_a_skip_flag(proj)
```

Missing/unreadable transcript_path is checked BEFORE gauge_paths is

even resolved -- there is no known gauge path yet, so this stays silent
even though a real (single) binding exists.

calls internal: _bound_work
reads internal: gw x2
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

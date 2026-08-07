# tests.test_gauge_writer:test_uncalibrated_flag_does_not_clobber_an_existing_reading
function, tests/test_gauge_writer.py:489, 9 lines

```python
def test_uncalibrated_flag_does_not_clobber_an_existing_reading(proj, tmp_path)
```

A good reading already on disk must survive; it ages into staleness on

its own, which the reader already collapses to no-reading.

calls internal: _hook_data x2, _bound_work, _unknown_model_transcript
reads internal: gw x2, _FIXTURE
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found

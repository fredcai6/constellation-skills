# tests.test_gauge_writer:test_uncalibrated_model_writes_no_reading
function, tests/test_gauge_writer.py:467, 8 lines

```python
def test_uncalibrated_model_writes_no_reading(proj, tmp_path)
```

The #252 regression. An unknown model previously divided its token count

by a 200k default and wrote that as a genuine fill — which read ~5x high
for the 1M-window models that are now the whole lineup, and tripped the
governor at ~14% of real capacity. There must be NO reading at all.

calls internal: _bound_work, _hook_data, _unknown_model_transcript
reads internal: gw
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found

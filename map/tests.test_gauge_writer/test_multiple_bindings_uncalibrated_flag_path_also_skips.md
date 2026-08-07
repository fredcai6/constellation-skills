# tests.test_gauge_writer:test_multiple_bindings_uncalibrated_flag_path_also_skips
function, tests/test_gauge_writer.py:357, 32 lines

```python
def test_multiple_bindings_uncalibrated_flag_path_also_skips(proj, tmp_path)
```

The uncalibrated-flag path is a second write path inside the same

handler -- it must skip on 2+ bindings too, not just the calibrated-record
path. Neither spine gets a gauge-uncalibrated.json flag.

calls internal: _bind x2, _hook_data
calls stdlib: json.dumps
reads internal: gw x3
reads stdlib: json (module)
unresolved: 10 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

# tests.test_gauge_writer:test_clean_write_clears_a_prior_skip_flag_at_that_path
function, tests/test_gauge_writer.py:623, 20 lines

```python
def test_clean_write_clears_a_prior_skip_flag_at_that_path(proj, tmp_path)
```

A path that was flagged no-usable-record on one call and then resolves

to a clean reading on the next call must have its skip flag cleared --
mirrors _clear_uncalibrated_flag exactly.

calls internal: _hook_data x2, _bind
calls stdlib: json.dumps
reads internal: gw x4, _FIXTURE
reads stdlib: json (module)
unresolved: 8 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

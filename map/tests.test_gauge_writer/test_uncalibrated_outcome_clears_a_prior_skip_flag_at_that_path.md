# tests.test_gauge_writer:test_uncalibrated_outcome_clears_a_prior_skip_flag_at_that_path
function, tests/test_gauge_writer.py:645, 15 lines

```python
def test_uncalibrated_outcome_clears_a_prior_skip_flag_at_that_path(proj, tmp_path)
```

The uncalibrated-flag write is also a 'resolved' outcome for this

path (a real, if unwindowed, usage record was found) -- it must clear a
stale skip flag too, not just a clean gauge.json write.

calls internal: _hook_data x2, _bound_work, _unknown_model_transcript
calls stdlib: json.dumps
reads internal: gw x5
reads stdlib: json (module)
unresolved: 6 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found

# tests.test_gauge_writer:test_flag_is_cleared_once_the_model_resolves
function, tests/test_gauge_writer.py:500, 10 lines

```python
def test_flag_is_cleared_once_the_model_resolves(proj, tmp_path)
```

Adding the missing row must actually silence the warning — otherwise the

fix leaves a permanent nag and people learn to ignore it.

calls internal: _hook_data x2, _bound_work, _unknown_model_transcript
reads internal: gw x4, _FIXTURE
unresolved: 5 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

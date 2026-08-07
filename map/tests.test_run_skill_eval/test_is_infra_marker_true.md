# tests.test_run_skill_eval:test_is_infra_marker_true
function, tests/test_run_skill_eval.py:298, 2 lines

```python
@pytest.mark.parametrize('text', ['hit the USAGE LIMIT', 'rate limit exceeded', 'quota reached', 'Overloaded', 'HTTP 429'])
def test_is_infra_marker_true(text)
```

HOLE: no docstring

reads internal: rse
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

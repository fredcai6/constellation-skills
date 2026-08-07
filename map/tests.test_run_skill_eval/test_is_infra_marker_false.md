# tests.test_run_skill_eval:test_is_infra_marker_false
function, tests/test_run_skill_eval.py:303, 2 lines

```python
@pytest.mark.parametrize('text', ['', 'AssertionError in test', 'exit code 1', None])
def test_is_infra_marker_false(text)
```

HOLE: no docstring

reads internal: rse
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

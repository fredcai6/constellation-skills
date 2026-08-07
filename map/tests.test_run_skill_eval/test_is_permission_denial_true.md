# tests.test_run_skill_eval:test_is_permission_denial_true
function, tests/test_run_skill_eval.py:320, 2 lines

```python
@pytest.mark.parametrize('text', ['Claude requested permissions to write', 'this action requires manual approval', 'requires approval before running', 'Permission denied', 'operation not permitted'])
def test_is_permission_denial_true(text)
```

HOLE: no docstring

reads internal: rse
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

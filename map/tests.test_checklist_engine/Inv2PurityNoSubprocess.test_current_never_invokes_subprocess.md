# tests.test_checklist_engine:Inv2PurityNoSubprocess.test_current_never_invokes_subprocess
method, tests/test_checklist_engine.py:4161, 21 lines

```python
def test_current_never_invokes_subprocess(self)
```

HOLE: no docstring

calls internal: Inv2PurityNoSubprocess.assertIn x3, gate, gated
calls stdlib: builtins.AssertionError
reads internal: E x2, FAIL_COMMAND x2
reads stdlib: unittest.mock, unittest.mock.patch
unresolved: 1 calls (chained-attribute), 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

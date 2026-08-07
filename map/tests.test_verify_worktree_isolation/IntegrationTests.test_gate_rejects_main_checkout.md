# tests.test_verify_worktree_isolation:IntegrationTests.test_gate_rejects_main_checkout
method, tests/test_verify_worktree_isolation.py:169, 3 lines

```python
def test_gate_rejects_main_checkout(self)
```

HOLE: no docstring

calls internal: IntegrationTests.assertEqual
calls stdlib: builtins.str, os.chdir
reads internal: IntegrationTests.repo x2, IntegrationTests.m
reads stdlib: os (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

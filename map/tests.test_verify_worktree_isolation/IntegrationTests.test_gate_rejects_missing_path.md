# tests.test_verify_worktree_isolation:IntegrationTests.test_gate_rejects_missing_path
method, tests/test_verify_worktree_isolation.py:173, 3 lines

```python
def test_gate_rejects_missing_path(self)
```

HOLE: no docstring

calls internal: IntegrationTests.assertEqual
calls stdlib: builtins.str, os.chdir
reads internal: IntegrationTests.repo x2, IntegrationTests.m
reads stdlib: os (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

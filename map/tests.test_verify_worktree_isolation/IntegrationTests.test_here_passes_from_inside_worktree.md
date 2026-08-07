# tests.test_verify_worktree_isolation:IntegrationTests.test_here_passes_from_inside_worktree
method, tests/test_verify_worktree_isolation.py:177, 3 lines

```python
def test_here_passes_from_inside_worktree(self)
```

HOLE: no docstring

calls internal: IntegrationTests.assertEqual
calls stdlib: builtins.str, os.chdir
reads internal: IntegrationTests.wt x2, IntegrationTests.m
reads stdlib: os (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

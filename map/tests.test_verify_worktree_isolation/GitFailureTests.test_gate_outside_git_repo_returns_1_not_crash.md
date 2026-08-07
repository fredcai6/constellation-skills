# tests.test_verify_worktree_isolation:GitFailureTests.test_gate_outside_git_repo_returns_1_not_crash
method, tests/test_verify_worktree_isolation.py:208, 5 lines

```python
def test_gate_outside_git_repo_returns_1_not_crash(self)
```

HOLE: no docstring

calls internal: GitFailureTests.assertEqual
calls stdlib: os.chdir
reads internal: GitFailureTests.tmp x2, GitFailureTests.m
reads stdlib: os (module)
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

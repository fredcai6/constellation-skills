# tests.test_verify_worktree_isolation:GitFailureTests.setUp
method, tests/test_verify_worktree_isolation.py:199, 4 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: load
calls stdlib: os.getcwd, tempfile.TemporaryDirectory
reads stdlib: os (module), tempfile (module)
writes internal: GitFailureTests._cwd, GitFailureTests.m, GitFailureTests.tmp

referenced by: none found

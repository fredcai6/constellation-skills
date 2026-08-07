# tests.test_verify_worktree_isolation:IntegrationTests.setUp
method, tests/test_verify_worktree_isolation.py:141, 13 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: IntegrationTests._git x3, load
calls stdlib: pathlib.Path x2, builtins.str, os.getcwd, tempfile.TemporaryDirectory
reads internal: IntegrationTests.tmp x2, IntegrationTests.repo, IntegrationTests.wt
reads stdlib: os (module), tempfile (module)
writes internal: IntegrationTests._cwd, IntegrationTests.m, IntegrationTests.repo, IntegrationTests.tmp, IntegrationTests.wt
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

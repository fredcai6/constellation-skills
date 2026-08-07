# tests.test_verify_worktree_isolation:IntegrationTests.tearDown
method, tests/test_verify_worktree_isolation.py:155, 3 lines

```python
def tearDown(self)
```

HOLE: no docstring

calls stdlib: os.chdir
reads internal: IntegrationTests._cwd, IntegrationTests.tmp
reads stdlib: os (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

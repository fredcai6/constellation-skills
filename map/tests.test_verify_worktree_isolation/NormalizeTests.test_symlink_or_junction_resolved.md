# tests.test_verify_worktree_isolation:NormalizeTests.test_symlink_or_junction_resolved
method, tests/test_verify_worktree_isolation.py:54, 14 lines

```python
def test_symlink_or_junction_resolved(self)
```

HOLE: no docstring

calls internal: NormalizeTests.assertEqual, NormalizeTests.skipTest
calls stdlib: os.path.join x2, os.mkdir, os.symlink, tempfile.TemporaryDirectory
reads internal: NormalizeTests.m x2
reads stdlib: os (module) x4, os.path x2, builtins.NotImplementedError, builtins.OSError, builtins.ValueError, tempfile (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found

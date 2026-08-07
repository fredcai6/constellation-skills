# tests.test_checklist_engine:PosixShellRoutingTests.test_find_posix_shell_guards_none_git
method, tests/test_checklist_engine.py:1205, 8 lines

```python
def test_find_posix_shell_guards_none_git(self)
```

HOLE: no docstring

calls internal: PosixShellRoutingTests.assertIsNone
calls stdlib: builtins.AssertionError
reads internal: E x4
reads stdlib: unittest.mock x3, unittest.mock.patch x3
unresolved: 3 calls (chained-attribute), 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

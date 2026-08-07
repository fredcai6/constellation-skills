# tests.test_checklist_engine:PosixShellRoutingTests.test_no_posix_shell_never_invokes_subprocess_run
method, tests/test_checklist_engine.py:1242, 10 lines

```python
def test_no_posix_shell_never_invokes_subprocess_run(self)
```

HOLE: no docstring

calls internal: PosixShellRoutingTests.assertEqual x2
calls stdlib: builtins.AssertionError
reads internal: E x3, PASS_COMMAND
reads stdlib: unittest.mock x2, unittest.mock.patch x2
unresolved: 2 calls (chained-attribute), 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

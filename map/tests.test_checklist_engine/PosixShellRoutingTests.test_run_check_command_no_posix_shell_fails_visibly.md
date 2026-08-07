# tests.test_checklist_engine:PosixShellRoutingTests.test_run_check_command_no_posix_shell_fails_visibly
method, tests/test_checklist_engine.py:1222, 9 lines

```python
def test_run_check_command_no_posix_shell_fails_visibly(self)
```

HOLE: no docstring

calls internal: PosixShellRoutingTests.assertEqual x2, PosixShellRoutingTests.assertIn
reads internal: E x2, PASS_COMMAND
reads stdlib: unittest.mock, unittest.mock.patch
unresolved: 1 calls (chained-attribute), 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

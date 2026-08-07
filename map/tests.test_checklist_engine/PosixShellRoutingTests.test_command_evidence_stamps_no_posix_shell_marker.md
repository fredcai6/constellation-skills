# tests.test_checklist_engine:PosixShellRoutingTests.test_command_evidence_stamps_no_posix_shell_marker
method, tests/test_checklist_engine.py:1232, 9 lines

```python
def test_command_evidence_stamps_no_posix_shell_marker(self)
```

HOLE: no docstring

calls internal: PosixShellRoutingTests.assertEqual x2, PosixShellRoutingTests.assertRaises, gate, gated
reads internal: E x3, PASS_COMMAND
reads stdlib: unittest.mock, unittest.mock.patch
unresolved: 1 calls (chained-attribute), 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

# tests.test_checklist_engine:PosixShellRoutingTests.test_find_posix_shell_falls_back_to_sh_on_windows
method, tests/test_checklist_engine.py:1214, 7 lines

```python
def test_find_posix_shell_falls_back_to_sh_on_windows(self)
```

HOLE: no docstring

calls internal: PosixShellRoutingTests.assertEqual
reads internal: E x3
reads stdlib: unittest.mock x2, unittest.mock.patch x2
unresolved: 2 calls (chained-attribute), 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base), 1 reads (unbound-name)

referenced by: none found

# tests.test_install_constellation:InterpreterProbeTests.test_probe_falls_through_to_next_candidate_when_py_is_unresolvable
method, tests/test_install_constellation.py:998, 45 lines

```python
def test_probe_falls_through_to_next_candidate_when_py_is_unresolvable(self)
```

HOLE: no docstring

calls internal: InterpreterProbeTests.skipTest x2, InterpreterProbeTests.assertIn, InterpreterProbeTests.assertNotEqual, _find_py_free_interpreter_dir, load_installer
calls stdlib: builtins.str
reads stdlib: os (module), os.environ, unittest.mock, unittest.mock.patch
unresolved: 1 calls (chained-attribute), 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

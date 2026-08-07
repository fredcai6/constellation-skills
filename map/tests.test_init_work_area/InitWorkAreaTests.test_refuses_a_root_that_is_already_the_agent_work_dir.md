# tests.test_init_work_area:InitWorkAreaTests.test_refuses_a_root_that_is_already_the_agent_work_dir
method, tests/test_init_work_area.py:90, 12 lines

```python
def test_refuses_a_root_that_is_already_the_agent_work_dir(self)
```

HOLE: no docstring

calls internal: InitWorkAreaTests.assertFalse, InitWorkAreaTests.assertIn, InitWorkAreaTests.assertRaises, load
calls stdlib: builtins.str, pathlib.Path, tempfile.TemporaryDirectory
reads stdlib: builtins.SystemExit, tempfile (module)
unresolved: 3 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

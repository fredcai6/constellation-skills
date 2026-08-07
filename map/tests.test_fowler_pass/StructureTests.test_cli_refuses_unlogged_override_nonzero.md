# tests.test_fowler_pass:StructureTests.test_cli_refuses_unlogged_override_nonzero
method, tests/test_fowler_pass.py:240, 6 lines

```python
def test_cli_refuses_unlogged_override_nonzero(self)
```

HOLE: no docstring

calls internal: StructureTests.assertNotEqual, _record, _with
calls stdlib: builtins.str, json.dumps, pathlib.Path, tempfile.TemporaryDirectory
reads internal: StructureTests.rail
reads stdlib: json (module), tempfile (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found

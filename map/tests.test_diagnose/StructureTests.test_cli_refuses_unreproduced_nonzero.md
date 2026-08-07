# tests.test_diagnose:StructureTests.test_cli_refuses_unreproduced_nonzero
method, tests/test_diagnose.py:260, 8 lines

```python
def test_cli_refuses_unreproduced_nonzero(self)
```

HOLE: no docstring

calls internal: StructureTests.assertNotEqual
calls stdlib: builtins.str, json.dumps, pathlib.Path, tempfile.TemporaryDirectory
reads internal: StructureTests.rail
reads stdlib: json (module), tempfile (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found

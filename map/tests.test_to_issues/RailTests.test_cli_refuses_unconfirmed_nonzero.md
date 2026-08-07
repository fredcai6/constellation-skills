# tests.test_to_issues:RailTests.test_cli_refuses_unconfirmed_nonzero
method, tests/test_to_issues.py:147, 6 lines

```python
def test_cli_refuses_unconfirmed_nonzero(self)
```

HOLE: no docstring

calls internal: RailTests.assertNotEqual, _write, well_formed_manifest
calls stdlib: builtins.str x2, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RailTests.rail, UNCONFIRMED_SPEC
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

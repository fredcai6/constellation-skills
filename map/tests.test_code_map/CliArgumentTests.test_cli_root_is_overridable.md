# tests.test_code_map:CliArgumentTests.test_cli_root_is_overridable
method, tests/test_code_map.py:137, 3 lines

```python
def test_cli_root_is_overridable(self)
```

HOLE: no docstring

calls internal: CliArgumentTests.assertEqual
calls cross-module: scripts.code_map.cli:build_parser
calls stdlib: pathlib.Path x2
reads cross-module: scripts.code_map.cli:
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

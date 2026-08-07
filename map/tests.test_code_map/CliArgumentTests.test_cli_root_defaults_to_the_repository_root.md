# tests.test_code_map:CliArgumentTests.test_cli_root_defaults_to_the_repository_root
method, tests/test_code_map.py:133, 3 lines

```python
def test_cli_root_defaults_to_the_repository_root(self)
```

HOLE: no docstring

calls internal: CliArgumentTests.assertEqual
calls cross-module: scripts.code_map.cli:build_parser
calls stdlib: pathlib.Path
reads internal: ROOT
reads cross-module: scripts.code_map.cli:
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

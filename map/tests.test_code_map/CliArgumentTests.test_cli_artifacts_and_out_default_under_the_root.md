# tests.test_code_map:CliArgumentTests.test_cli_artifacts_and_out_default_under_the_root
method, tests/test_code_map.py:153, 4 lines

```python
def test_cli_artifacts_and_out_default_under_the_root(self)
```

HOLE: no docstring

calls internal: CliArgumentTests.assertEqual x2
calls cross-module: scripts.code_map.cli:build_parser
calls stdlib: pathlib.Path x4
reads cross-module: scripts.code_map.cli:
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

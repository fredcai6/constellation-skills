# tests.test_code_map:CliArgumentTests.test_cli_requires_a_subcommand
method, tests/test_code_map.py:147, 5 lines

```python
def test_cli_requires_a_subcommand(self)
```

HOLE: no docstring

calls internal: CliArgumentTests.assertEqual, CliArgumentTests.assertRaises
calls cross-module: scripts.code_map.cli:build_parser
calls stdlib: contextlib.redirect_stderr, io.StringIO
reads cross-module: scripts.code_map.cli:
reads stdlib: builtins.SystemExit, contextlib (module), io (module)
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

# tests.test_code_map:CliDiscoverCommandTests.test_cli_discover_prints_the_mappable_corpus_and_exits_zero
method, tests/test_code_map.py:171, 6 lines

```python
def test_cli_discover_prints_the_mappable_corpus_and_exits_zero(self)
```

HOLE: no docstring

calls internal: CliDiscoverCommandTests.assertEqual x2
calls cross-module: scripts.code_map.cli:main
calls stdlib: builtins.str, contextlib.redirect_stdout, io.StringIO
reads internal: CliDiscoverCommandTests.repo
reads cross-module: scripts.code_map.cli:
reads stdlib: contextlib (module), io (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found

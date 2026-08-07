# tests.test_context_declaration_lint:CliTests._write_fixture
method, tests/test_context_declaration_lint.py:161, 4 lines

```python
def _write_fixture(self, key: str) -> str
```

HOLE: no docstring

calls stdlib: builtins.str, json.dumps, pathlib.Path
reads internal: CliTests.tmp, FIXTURES
reads stdlib: json (module)
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only

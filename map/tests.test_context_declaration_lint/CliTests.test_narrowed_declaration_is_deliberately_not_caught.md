# tests.test_context_declaration_lint:CliTests.test_narrowed_declaration_is_deliberately_not_caught
method, tests/test_context_declaration_lint.py:191, 21 lines

```python
def test_narrowed_declaration_is_deliberately_not_caught(self)
```

HOLE: no docstring

calls internal: CliTests._write_fixture, CliTests.assertEqual
calls stdlib: contextlib.redirect_stdout, io.StringIO
reads internal: CliTests.m
reads stdlib: contextlib (module), io (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

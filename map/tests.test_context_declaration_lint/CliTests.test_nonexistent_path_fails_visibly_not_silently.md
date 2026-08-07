# tests.test_context_declaration_lint:CliTests.test_nonexistent_path_fails_visibly_not_silently
method, tests/test_context_declaration_lint.py:184, 6 lines

```python
def test_nonexistent_path_fails_visibly_not_silently(self)
```

HOLE: no docstring

calls internal: CliTests.assertNotEqual
calls stdlib: builtins.str, contextlib.redirect_stderr, io.StringIO, pathlib.Path
reads internal: CliTests.m, CliTests.tmp
reads stdlib: contextlib (module), io (module)
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found

# tests.test_context_declaration_lint:CliTests.setUp
method, tests/test_context_declaration_lint.py:156, 4 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: CliTests.addCleanup, load
calls stdlib: tempfile.TemporaryDirectory
reads internal: CliTests.tmp
writes internal: CliTests.m, CliTests.tmp
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found

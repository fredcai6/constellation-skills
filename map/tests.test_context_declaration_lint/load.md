# tests.test_context_declaration_lint:load
function, tests/test_context_declaration_lint.py:31, 7 lines

```python
def load()
```

HOLE: no docstring

calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location
reads internal: ROOT
reads stdlib: importlib (module) x2, importlib.util x2
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 4 sites, this module only

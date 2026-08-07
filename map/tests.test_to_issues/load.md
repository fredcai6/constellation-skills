# tests.test_to_issues:load
function, tests/test_to_issues.py:23, 5 lines

```python
def load(name: str)
```

HOLE: no docstring

calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location
reads internal: ROOT
reads stdlib: importlib (module) x2, importlib.util x2
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only

# tests.test_interrogation:load
function, tests/test_interrogation.py:35, 5 lines

```python
def load(name: str)
```

HOLE: no docstring

calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location
reads internal: ROOT
reads stdlib: importlib (module) x2, importlib.util x2
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 5 sites, this module only

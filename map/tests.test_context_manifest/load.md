# tests.test_context_manifest:load
function, tests/test_context_manifest.py:23, 6 lines

```python
def load(name)
```

HOLE: no docstring

calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location
reads internal: ROOT
reads stdlib: importlib (module) x2, importlib.util x2, sys (module), sys.modules
writes stdlib: sys.modules[]
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only

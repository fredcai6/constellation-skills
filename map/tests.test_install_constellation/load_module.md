# tests.test_install_constellation:load_module
function, tests/test_install_constellation.py:21, 6 lines

```python
def load_module(name: str, path: Path)
```

HOLE: no docstring

calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location
reads stdlib: importlib (module) x2, importlib.util x2, sys (module), sys.modules
writes stdlib: sys.modules[]
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 6 sites, this module only

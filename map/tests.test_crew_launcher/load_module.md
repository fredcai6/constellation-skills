# tests.test_crew_launcher:load_module
function, tests/test_crew_launcher.py:33, 6 lines

```python
def load_module(name: str, path: Path)
```

HOLE: no docstring

calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location
reads stdlib: importlib (module) x2, importlib.util x2, sys (module), sys.modules
writes stdlib: sys.modules[]
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only

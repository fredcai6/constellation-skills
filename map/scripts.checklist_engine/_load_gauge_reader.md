# scripts.checklist_engine:_load_gauge_reader
function, scripts/checklist_engine.py:85, 13 lines

```python
def _load_gauge_reader()
```

HOLE: no docstring

calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location, pathlib.Path
reads stdlib: importlib (module) x2, importlib.util x2, builtins.Exception, sys (module), sys.modules
writes stdlib: sys.modules[]
unresolved: 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base), 1 reads (unbound-name)

referenced by: 1 sites, this module only

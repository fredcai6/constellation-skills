# scripts.run_skill_eval:_load_install_constellation
function, scripts/run_skill_eval.py:56, 13 lines

```python
def _load_install_constellation()
```

HOLE: no docstring

calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location
reads internal: _HERE
reads stdlib: sys (module) x3, sys.modules x3, importlib (module) x2, importlib.util x2
writes stdlib: sys.modules[]
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

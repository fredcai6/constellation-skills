# tests.test_episode_store:load_query
function, tests/test_episode_store.py:40, 6 lines

```python
def load_query()
```

HOLE: no docstring

calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location
reads internal: QUERY_SCRIPT
reads stdlib: importlib (module) x2, importlib.util x2, sys (module), sys.modules
writes stdlib: sys.modules[]
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only

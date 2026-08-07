# tests.test_check_corpus_freshness:load_checker
function, tests/test_check_corpus_freshness.py:18, 12 lines

```python
def load_checker()
```

HOLE: no docstring

calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location
reads internal: CHECKER
reads stdlib: importlib (module) x2, importlib.util x2, sys (module), sys.modules
writes stdlib: sys.modules[]
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only

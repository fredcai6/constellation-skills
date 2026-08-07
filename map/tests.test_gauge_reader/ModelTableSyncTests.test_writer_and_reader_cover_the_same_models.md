# tests.test_gauge_reader:ModelTableSyncTests.test_writer_and_reader_cover_the_same_models
method, tests/test_gauge_reader.py:85, 9 lines

```python
def test_writer_and_reader_cover_the_same_models(self)
```

HOLE: no docstring

calls internal: ModelTableSyncTests.assertEqual, load
calls stdlib: builtins.set x2, importlib.util.module_from_spec, importlib.util.spec_from_file_location
reads internal: ROOT
reads stdlib: importlib (module) x2, importlib.util x2, sys (module), sys.modules
writes stdlib: sys.modules[]
unresolved: 1 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found

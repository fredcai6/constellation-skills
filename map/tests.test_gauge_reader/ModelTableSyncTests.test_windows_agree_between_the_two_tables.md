# tests.test_gauge_reader:ModelTableSyncTests.test_windows_agree_between_the_two_tables
method, tests/test_gauge_reader.py:95, 12 lines

```python
def test_windows_agree_between_the_two_tables(self)
```

The reader stores the window alongside its caps; a disagreement

would make the same model read at two different scales.

calls internal: ModelTableSyncTests.assertEqual, load
calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location
reads internal: ROOT
reads stdlib: importlib (module) x2, importlib.util x2, sys (module), sys.modules
writes stdlib: sys.modules[]
unresolved: 2 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found

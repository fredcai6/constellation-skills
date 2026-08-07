# tests.test_episode_store:AbsentStoreTests.test_a_missing_layout_directory_is_refused_rather_than_read_as_empty
method, tests/test_episode_store.py:2465, 16 lines

```python
def test_a_missing_layout_directory_is_refused_rather_than_read_as_empty(self)
```

HOLE: no docstring

calls internal: AbsentStoreTests.assertIn x3, QueryTestCase.seed x2, AbsentStoreTests.assertNotEqual, AbsentStoreTests.assertRaises, AbsentStoreTests.assertTrue, QueryTestCase.retire, QueryTestCase.run_query, episode_path
calls stdlib: builtins.str x2, shutil.rmtree
reads internal: AbsentStoreTests.root x3, AbsentStoreTests.last_stderr, AbsentStoreTests.m, AbsentStoreTests.q
reads stdlib: shutil (module)
unresolved: 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found

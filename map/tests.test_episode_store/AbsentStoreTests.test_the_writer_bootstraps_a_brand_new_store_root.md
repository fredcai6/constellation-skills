# tests.test_episode_store:AbsentStoreTests.test_the_writer_bootstraps_a_brand_new_store_root
method, tests/test_episode_store.py:2488, 14 lines

```python
def test_the_writer_bootstraps_a_brand_new_store_root(self)
```

The other half of the rule: a create into a store root that does not exist yet

must still work, because that is how a store comes into being at all.

calls internal: AbsentStoreTests.assertEqual x2, AbsentStoreTests.assertTrue x2, create_op
calls stdlib: builtins.str x2, pathlib.Path x2, json.dumps
reads internal: AbsentStoreTests.tmp x2, AbsentStoreTests.m, AbsentStoreTests.q
reads stdlib: json (module)
unresolved: 5 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found

# tests.test_episode_store:CrossSessionRetrievalTests.test_episode_seeded_in_one_process_is_retrievable_in_a_freshly_booted_one
method, tests/test_episode_store.py:1224, 37 lines

```python
def test_episode_seeded_in_one_process_is_retrievable_in_a_freshly_booted_one(self)
```

HOLE: no docstring

calls internal: CrossSessionRetrievalTests.assertEqual x7, CrossSessionRetrievalTests.assertNotEqual, CrossSessionRetrievalTests.assertNotIn, SeparateProcessMixin.run_in_separate_process, SeparateProcessMixin.seed_in_separate_process, create_op
calls stdlib: builtins.str, json.loads, os.getpid
reads internal: CrossSessionRetrievalTests.root x2, CrossSessionRetrievalTests.tmp x2, QUERY_SCRIPT
reads stdlib: json (module), os (module)
unresolved: 2 reads (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: none found

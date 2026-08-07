# tests.test_episode_store:HalfRetirementSafetyTests.test_a_half_retired_store_is_reported_rather_than_answered_around
method, tests/test_episode_store.py:2082, 29 lines

```python
def test_a_half_retired_store_is_reported_rather_than_answered_around(self)
```

Compensation covers every failure the process survives to observe; a hard kill

between the two steps runs no compensation at all, and markdown-in-git offers no
journal to close that. So the residual state is made LOUD rather than claimed
impossible: retrieval refuses instead of returning an answer that silently picks
one of the two copies.

calls internal: HalfRetirementSafetyTests.assertIn x3, episode_path x3, HalfRetirementSafetyTests.assertEqual x2, EpisodeStoreTestCase.run_delta, HalfRetirementSafetyTests.assertRaises, QueryTestCase.run_query, QueryTestCase.seed, create_op
calls stdlib: builtins.str x2, shutil.copyfile
reads internal: HalfRetirementSafetyTests.root x6, HalfRetirementSafetyTests.q x3, HalfRetirementSafetyTests.last_stderr, HalfRetirementSafetyTests.m
reads stdlib: shutil (module)
unresolved: 5 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found

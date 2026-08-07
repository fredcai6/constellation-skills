# tests.test_episode_store:HalfRetirementSafetyTests.assert_consistent
method, tests/test_episode_store.py:1982, 18 lines

```python
def assert_consistent(self, episode_id)
```

The invariant, stated once: an id is in EXACTLY ONE of the two sets, and the

`status` recorded inside the file agrees with the directory holding it.

calls internal: HalfRetirementSafetyTests._sets, HalfRetirementSafetyTests.assertEqual, HalfRetirementSafetyTests.assertIsNotNone, HalfRetirementSafetyTests.assertNotEqual
reads internal: HalfRetirementSafetyTests.q, HalfRetirementSafetyTests.root
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only

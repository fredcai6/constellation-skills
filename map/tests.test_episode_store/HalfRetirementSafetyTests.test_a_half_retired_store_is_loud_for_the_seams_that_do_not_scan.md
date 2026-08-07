# tests.test_episode_store:HalfRetirementSafetyTests.test_a_half_retired_store_is_loud_for_the_seams_that_do_not_scan
method, tests/test_episode_store.py:2112, 62 lines

```python
def test_a_half_retired_store_is_loud_for_the_seams_that_do_not_scan(self)
```

The other half of "loud", and the half that was missing.

A scanning reader meets the enumeration seam and refuses. `fetch` does not scan —
it resolves one path — and the writer's `retire` does not scan either, so both
used to proceed against a store the store itself had already declared corrupt:
`fetch` silently returned the `active/` copy with `status: active`, and a retire
committed on top of it. Loud in one hand and silent in the other is worse than
either, because the silent hand is the one #308's consolidation pass walks back
through when it follows a `consolidated-into:` reference by id.

calls internal: episode_path x5, EpisodeStoreTestCase.run_delta x4, HalfRetirementSafetyTests.assertIn x3, HalfRetirementSafetyTests.assertRaises x2, QueryTestCase.seed x2, read_exact x2, HalfRetirementSafetyTests.assertEqual, HalfRetirementSafetyTests.assertIsNotNone, QueryTestCase.run_query, create_op
calls stdlib: builtins.str x2, shutil.copyfile
reads internal: HalfRetirementSafetyTests.root x8, HalfRetirementSafetyTests.m x3, HalfRetirementSafetyTests.q x2, HalfRetirementSafetyTests.last_stderr
reads stdlib: shutil (module)
unresolved: 5 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: none found

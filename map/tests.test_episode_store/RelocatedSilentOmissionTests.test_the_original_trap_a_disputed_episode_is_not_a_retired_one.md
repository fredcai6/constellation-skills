# tests.test_episode_store:RelocatedSilentOmissionTests.test_the_original_trap_a_disputed_episode_is_not_a_retired_one
method, tests/test_episode_store.py:2381, 26 lines

```python
def test_the_original_trap_a_disputed_episode_is_not_a_retired_one(self)
```

The fixture that started this whole thread, carried forward. An episode whose

core assertion is `disputed` is in a legitimate lifecycle state that is NEITHER
active nor retired, and it must still appear in ordinary search — retirement is
an episode-level search-visibility switch, `lifecycle-standing` is a per-assertion
epistemic judgement, and conflating them is what dropped the record.

calls internal: RelocatedSilentOmissionTests.assertEqual x2, EpisodeStoreTestCase.run_delta, QueryTestCase.seed, RelocatedSilentOmissionTests.assertIn, RelocatedSilentOmissionTests.assertTrue
reads internal: RelocatedSilentOmissionTests.root x3, RelocatedSilentOmissionTests.q x2, RelocatedSilentOmissionTests.m
unresolved: 3 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found

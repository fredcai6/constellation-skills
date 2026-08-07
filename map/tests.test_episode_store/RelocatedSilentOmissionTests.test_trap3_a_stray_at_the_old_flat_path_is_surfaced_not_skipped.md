# tests.test_episode_store:RelocatedSilentOmissionTests.test_trap3_a_stray_at_the_old_flat_path_is_surfaced_not_skipped
method, tests/test_episode_store.py:2213, 39 lines

```python
def test_trap3_a_stray_at_the_old_flat_path_is_surfaced_not_skipped(self)
```

The real migration hazard, and the one most likely to be missed.

A file at `episodes/<id>.md` is in NEITHER set. Ordinary retrieval does not see
it (it scans the ordinary set), and history-inclusive retrieval does not see it
either (it unions two directories this file is in neither of). It is therefore
invisible to every query while looking, to a human reading the directory, exactly
like a stored episode. Skipping it is a silent omission with a physical file
sitting right there as evidence.

calls internal: RelocatedSilentOmissionTests.assertIn x3, episode_path x2, EpisodeStoreTestCase.run_delta, QueryTestCase.run_query, QueryTestCase.seed, RelocatedSilentOmissionTests.assertEqual, RelocatedSilentOmissionTests.assertNotIn, RelocatedSilentOmissionTests.assertRaises, RelocatedSilentOmissionTests.assertTrue, create_op, naive_history_inclusive_forgetting_the_union
calls stdlib: builtins.str x4, builtins.sorted, shutil.copyfile, shutil.move
reads internal: RelocatedSilentOmissionTests.root x6, RelocatedSilentOmissionTests.q x2, RelocatedSilentOmissionTests.last_stderr, RelocatedSilentOmissionTests.m
reads stdlib: shutil (module) x2
unresolved: 3 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found

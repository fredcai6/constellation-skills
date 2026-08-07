# tests.test_episode_store:RelocatedSilentOmissionTests.test_a_forged_status_line_in_free_text_cannot_move_an_episode_between_sets
method, tests/test_episode_store.py:2408, 21 lines

```python
def test_a_forged_status_line_in_free_text_cannot_move_an_episode_between_sets(self)
```

Under the rejected Option B this needed a defense (a line-anchored filter, plus

the writer's single-line enforcement). Under Option A it is structurally
impossible — there is no status parse to fool, because membership is the
directory. Asserted rather than assumed, because "structurally impossible" is a
claim about the implementation, and implementations change.

calls internal: RelocatedSilentOmissionTests.assertEqual x2, EpisodeStoreTestCase.run_delta, RelocatedSilentOmissionTests.assertIn, RelocatedSilentOmissionTests.assertTrue, create_op, episode_path, naive_status_grep_membership, read_exact
reads internal: RelocatedSilentOmissionTests.root x4, RelocatedSilentOmissionTests.m, RelocatedSilentOmissionTests.q
unresolved: 2 calls (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: none found

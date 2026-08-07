# tests.test_episode_store:RelocatedSilentOmissionTests.test_trap4_a_non_episode_file_inside_a_layout_directory_is_refused
method, tests/test_episode_store.py:2278, 30 lines

```python
def test_trap4_a_non_episode_file_inside_a_layout_directory_is_refused(self)
```

The mirror image of trap 3, and the one that actually shipped.

Trap 3 is an adversarial input: an episode id at a path where no episode belongs.
Trap 4 is the direction that was missed — a NON-episode file at a path where the
store treats everything as an episode. Membership moved from file content to file
location, so a directory listing became the candidate set, and anything sitting in
the directory (a README, a `.gitkeep`, a `CODEOWNERS`) is minted into an id that
no record backs.

calls internal: RelocatedSilentOmissionTests.assertIn x4, EpisodeStoreTestCase.run_delta, QueryTestCase.run_query, QueryTestCase.seed, RelocatedSilentOmissionTests.assertEqual, RelocatedSilentOmissionTests.assertRaises, create_op, naive_layout_listing_as_ids
calls stdlib: builtins.str x2
reads internal: RelocatedSilentOmissionTests.root x4, RelocatedSilentOmissionTests.q x2, RelocatedSilentOmissionTests.last_stderr, RelocatedSilentOmissionTests.m
unresolved: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found

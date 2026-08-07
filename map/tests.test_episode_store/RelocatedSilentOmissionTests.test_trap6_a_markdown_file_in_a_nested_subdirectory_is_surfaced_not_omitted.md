# tests.test_episode_store:RelocatedSilentOmissionTests.test_trap6_a_markdown_file_in_a_nested_subdirectory_is_surfaced_not_omitted
method, tests/test_episode_store.py:2309, 39 lines

```python
def test_trap6_a_markdown_file_in_a_nested_subdirectory_is_surfaced_not_omitted(self)
```

Every scan in this store is one level deep, so anything a level further down

is invisible to all of them while looking exactly like a stored episode to a
human reading the tree. Two shapes, one class:

  episodes/archive/<id>.md      — a directory nobody declared
  episodes/active/old/<id>.md   — a subdirectory inside a layout directory

Neither is produced by anything today, which is precisely why it has to be
refused now: a hand-moved file, a half-finished migration, or a future tool is
what produces one, and by then the omission is silent and already shipped.

calls internal: RelocatedSilentOmissionTests.assertIn x2, RelocatedSilentOmissionTests.assertRaises x2, EpisodeStoreTestCase.run_delta, QueryTestCase.run_query, QueryTestCase.seed, RelocatedSilentOmissionTests.assertEqual, create_op, episode_path
calls stdlib: builtins.str x2, shutil.copyfile, shutil.rmtree
reads internal: RelocatedSilentOmissionTests.root x7, RelocatedSilentOmissionTests.q x3, RelocatedSilentOmissionTests.m x2
reads stdlib: shutil (module) x2
unresolved: 6 calls (dispatch-unknown-base), 8 reads (dispatch-unknown-base)

referenced by: none found

# tests.test_episode_store:QueryTestCase
class, tests/test_episode_store.py:706, 41 lines

```python
class QueryTestCase(EpisodeStoreTestCase)
```

Adds the retrieval module and a seeding helper to the writer's temp-store setup.

Deliberately a subclass rather than an edit of EpisodeStoreTestCase, so the g2 tests
keep exactly the setup they were written against.

- [setUp](QueryTestCase.setUp.md) method: HOLE: no docstring
- [seed](QueryTestCase.seed.md) method: Write one episode through the ONLY write path (g2's validated delta writer)
- [retire](QueryTestCase.retire.md) method: Retire one episode through the only write path, and return its id.
- [run_query](QueryTestCase.run_query.md) method: Drive query_episodes.py's CLI in-process and return its parsed JSON envelope.

referenced by: none found

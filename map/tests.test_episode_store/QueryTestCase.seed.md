# tests.test_episode_store:QueryTestCase.seed
method, tests/test_episode_store.py:715, 13 lines

```python
def seed(self, run='governor-268', **mechanical)
```

Write one episode through the ONLY write path (g2's validated delta writer)

and return its assigned id. Retrieval is never tested against a hand-authored
file — a fixture the writer could not have produced would prove nothing about
retrieval over the real store.

calls internal: EpisodeStoreTestCase.run_delta, QueryTestCase.assertEqual, create_op
calls stdlib: builtins.set x2, builtins.len
reads internal: QueryTestCase.q x2, QueryTestCase.root x2
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 86 sites, this module only

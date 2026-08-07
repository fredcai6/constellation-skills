# tests.test_episode_store:QueryTestCase.retire
method, tests/test_episode_store.py:729, 6 lines

```python
def retire(self, episode_id, reason='consolidated into a pattern episode')
```

Retire one episode through the only write path, and return its id.

calls internal: EpisodeStoreTestCase.run_delta

referenced by: 15 sites, this module only

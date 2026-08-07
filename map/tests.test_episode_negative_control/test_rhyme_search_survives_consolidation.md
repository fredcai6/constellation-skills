# tests.test_episode_negative_control:test_rhyme_search_survives_consolidation
function, tests/test_episode_negative_control.py:1069, 33 lines

```python
def test_rhyme_search_survives_consolidation(seeded_store)
```

Mark one cluster member CONSOLIDATED, then confirm rhyme-search still finds its

neighbours. This is the property #308's consolidation pass depends on.

calls third-party: query_episodes.neighbour_ids x4, apply_episode_delta.apply_delta, query_episodes.fetch_episode
reads third-party: query_episodes (module) x5, apply_episode_delta (module)
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found

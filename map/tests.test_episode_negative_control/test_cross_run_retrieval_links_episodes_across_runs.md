# tests.test_episode_negative_control:test_cross_run_retrieval_links_episodes_across_runs
function, tests/test_episode_negative_control.py:1056, 11 lines

```python
def test_cross_run_retrieval_links_episodes_across_runs(seeded_store)
```

The acceptance surface: an episode written by one run is reachable from another

episode of that cluster, and the unrelated run is NOT dragged in.

calls stdlib: builtins.sorted
calls third-party: query_episodes.neighbour_ids x2, query_episodes.enumerate_episode_ids
reads third-party: query_episodes (module) x3

referenced by: none found

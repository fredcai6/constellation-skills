# tests.test_episode_negative_control:test_321_observation_where_a_handed_id_is_validated
function, tests/test_episode_negative_control.py:1104, 23 lines

```python
def test_321_observation_where_a_handed_id_is_validated(seeded_store)
```

#321: the store validates ids it LISTS but not every id it is HANDED.

Recorded as an OBSERVATION for the Commander to rule on — deliberately NOT fixed here.

calls internal: _create_op
calls third-party: pytest.raises x3, apply_episode_delta.validate_delta x2, query_episodes.fetch_episode, query_episodes.neighbours
reads third-party: apply_episode_delta (module) x4, pytest (module) x3, query_episodes (module) x3, apply_episode_delta.EpisodeDeltaError x2, query_episodes.EpisodeNotFound

referenced by: none found

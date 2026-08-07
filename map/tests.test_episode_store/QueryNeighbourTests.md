# tests.test_episode_store:QueryNeighbourTests
class, tests/test_episode_store.py:1113, 54 lines

```python
class QueryNeighbourTests(QueryTestCase)
```

Enumerate neighbours — for episode E, every OTHER episode sharing at least one

exact join key with E (EPISODE_STORE.md section 8). The union IS the candidate set a
downstream sensor consumes: complete by construction, unranked, self excluded.

- [test_neighbours_by_shared_artifact_ref](QueryNeighbourTests.test_neighbours_by_shared_artifact_ref.md) method: HOLE: no docstring
- [test_neighbours_by_shared_role_and_spine_step_pair](QueryNeighbourTests.test_neighbours_by_shared_role_and_spine_step_pair.md) method: HOLE: no docstring
- [test_an_episode_is_never_its_own_neighbour](QueryNeighbourTests.test_an_episode_is_never_its_own_neighbour.md) method: HOLE: no docstring
- [test_neighbours_of_an_unknown_episode_fails_visibly](QueryNeighbourTests.test_neighbours_of_an_unknown_episode_fails_visibly.md) method: HOLE: no docstring
- [test_naive_first_key_wins_silently_omits_the_other_join_key](QueryNeighbourTests.test_naive_first_key_wins_silently_omits_the_other_join_key.md) method: HOLE: no docstring
- [test_neighbours_cli_envelope](QueryNeighbourTests.test_neighbours_cli_envelope.md) method: HOLE: no docstring

referenced by: none found

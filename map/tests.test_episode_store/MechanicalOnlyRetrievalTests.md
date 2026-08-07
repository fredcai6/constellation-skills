# tests.test_episode_store:MechanicalOnlyRetrievalTests
class, tests/test_episode_store.py:1675, 64 lines

```python
class MechanicalOnlyRetrievalTests(QueryTestCase)
```

C5 — retrieval is exact-match and set-membership only (EPISODE_STORE.md section

8). No ranking, no scoring, no similarity, no embedding. What a downstream sensor
receives is a complete, unordered candidate set; the stochastic judgment happens on
top of this surface, never inside it (B0.1, the stochastic boundary).

- [test_the_candidate_set_does_not_depend_on_the_order_episodes_were_written](MechanicalOnlyRetrievalTests.test_the_candidate_set_does_not_depend_on_the_order_episodes_were_written.md) method: HOLE: no docstring
- [test_results_carry_no_score_rank_or_similarity_field](MechanicalOnlyRetrievalTests.test_results_carry_no_score_rank_or_similarity_field.md) method: HOLE: no docstring
- [test_the_module_imports_no_ranking_or_embedding_machinery](MechanicalOnlyRetrievalTests.test_the_module_imports_no_ranking_or_embedding_machinery.md) method: HOLE: no docstring
- [test_neighbours_are_not_ordered_by_how_many_join_keys_they_share](MechanicalOnlyRetrievalTests.test_neighbours_are_not_ordered_by_how_many_join_keys_they_share.md) method: HOLE: no docstring

referenced by: none found

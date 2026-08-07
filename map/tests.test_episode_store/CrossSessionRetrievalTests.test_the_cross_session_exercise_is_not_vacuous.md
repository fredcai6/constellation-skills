# tests.test_episode_store:CrossSessionRetrievalTests.test_the_cross_session_exercise_is_not_vacuous
method, tests/test_episode_store.py:1262, 19 lines

```python
def test_the_cross_session_exercise_is_not_vacuous(self)
```

Falsification guard. The test above would be worthless if the retrieving

process could answer without the store — so point an identical session 2 at a
DIFFERENT, empty store root and confirm it fails to find the episode. What
carries the episode across the boundary is the store on disk and nothing else.

calls internal: CrossSessionRetrievalTests.assertEqual, CrossSessionRetrievalTests.assertIn, SeparateProcessMixin.run_in_separate_process, SeparateProcessMixin.seed_in_separate_process, create_op
calls stdlib: builtins.str, pathlib.Path
reads internal: CrossSessionRetrievalTests.tmp x3, CrossSessionRetrievalTests.m, CrossSessionRetrievalTests.root, QUERY_SCRIPT
unresolved: 1 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found

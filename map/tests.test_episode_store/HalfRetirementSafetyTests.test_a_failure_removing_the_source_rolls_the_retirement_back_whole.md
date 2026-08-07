# tests.test_episode_store:HalfRetirementSafetyTests.test_a_failure_removing_the_source_rolls_the_retirement_back_whole
method, tests/test_episode_store.py:2040, 41 lines

```python
def test_a_failure_removing_the_source_rolls_the_retirement_back_whole(self)
```

The window binding Option A actually opened, and the one this gate owes.

The archived file has already landed. If removing the source then fails, the
naive sequence leaves the id in BOTH directories: retired by content, still in
the ordinary-search set by directory. The placement phase compensates instead —
it restores the prior bytes of everything it disturbed and deletes what it newly
created, so the retirement is undone whole rather than left half-applied.

- [failing_remove](HalfRetirementSafetyTests.test_a_failure_removing_the_source_rolls_the_retirement_back_whole.failing_remove.md) method: HOLE: no docstring

calls internal: HalfRetirementSafetyTests.assertEqual x3, episode_path x3, read_exact x2, EpisodeStoreTestCase.run_delta, HalfRetirementSafetyTests.assertFalse, HalfRetirementSafetyTests.assert_consistent, QueryTestCase.seed
calls stdlib: builtins.sorted
reads internal: HalfRetirementSafetyTests.root x4, HalfRetirementSafetyTests.m x3
unresolved: 3 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base), 2 writes (dispatch-unknown-base)

referenced by: none found

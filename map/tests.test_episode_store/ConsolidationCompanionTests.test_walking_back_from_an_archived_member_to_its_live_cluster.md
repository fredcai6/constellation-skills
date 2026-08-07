# tests.test_episode_store:ConsolidationCompanionTests.test_walking_back_from_an_archived_member_to_its_live_cluster
method, tests/test_episode_store.py:2622, 7 lines

```python
def test_walking_back_from_an_archived_member_to_its_live_cluster(self)
```

The move #308 actually needs: start from a retired episode (the anchor is

fetched by id, so retirement does not hide it from itself) and recover the live
members it was consolidated with.

calls internal: ConsolidationCompanionTests.assertEqual, ConsolidationCompanionTests.cluster, QueryTestCase.retire
calls stdlib: builtins.sorted
reads internal: ConsolidationCompanionTests.q, ConsolidationCompanionTests.root
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

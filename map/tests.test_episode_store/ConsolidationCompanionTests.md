# tests.test_episode_store:ConsolidationCompanionTests
class, tests/test_episode_store.py:2574, 68 lines

```python
class ConsolidationCompanionTests(QueryTestCase)
```

C5 — the #308 companion is not precluded.

Consolidation is issue #308's job and is deliberately NOT built here. What this gate
owes is that the store leaves it possible: with one member of a cluster retired, the
surviving members stay findable by ordinary retrieval, and the retired member stays
reachable — by id, by history-inclusive scan, and from its own neighbourhood.

The failure this guards against is subtle. If retiring one member cost the cluster
its findability, a consolidation pass would be a one-way door: consolidate once, and
the evidence for whether the consolidation was right becomes unreachable.

- [cluster](ConsolidationCompanionTests.cluster.md) method: Three episodes joined on a shared artifact-ref — the join key section 6 already
- [test_retiring_one_member_leaves_the_rest_findable_ordinarily](ConsolidationCompanionTests.test_retiring_one_member_leaves_the_rest_findable_ordinarily.md) method: HOLE: no docstring
- [test_the_retired_member_stays_reachable_three_ways](ConsolidationCompanionTests.test_the_retired_member_stays_reachable_three_ways.md) method: HOLE: no docstring
- [test_walking_back_from_an_archived_member_to_its_live_cluster](ConsolidationCompanionTests.test_walking_back_from_an_archived_member_to_its_live_cluster.md) method: The move #308 actually needs: start from a retired episode (the anchor is
- [test_retiring_every_member_loses_nothing](ConsolidationCompanionTests.test_retiring_every_member_loses_nothing.md) method: HOLE: no docstring

referenced by: none found

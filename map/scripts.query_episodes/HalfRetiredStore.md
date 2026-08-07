# scripts.query_episodes:HalfRetiredStore
class, scripts/query_episodes.py:169, 6 lines

```python
class HalfRetiredStore(QueryError)
```

The base scan and the membership predicate disagree about one id. Under the bound

layout they are two reads of the same filesystem fact, so a disagreement means the
store is mid-move (an interrupted retirement) or the two seams have drifted apart.
Either way it is reported, never resolved by dropping the id — a candidate set that
quietly loses a record is the one outcome this module refuses.

referenced by: 1 sites, this module only

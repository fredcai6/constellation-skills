# scripts.query_episodes:QueryError
class, scripts/query_episodes.py:124, 4 lines

```python
class QueryError(Exception)
```

Raised when a query cannot be answered. Never swallowed into an empty result —

an unanswerable query and a query with no matches are different facts, and
collapsing them is how a silent omission gets shipped.

referenced by: 5 sites, this module only

# scripts.query_episodes:EpisodeNotFound
class, scripts/query_episodes.py:130, 4 lines

```python
class EpisodeNotFound(QueryError)
```

The named episode does not exist. A distinct type (and a distinct CLI exit code)

from an invalid query, so a caller can tell "there is no such episode" from "your
query was malformed" — and neither from "nothing matched".

referenced by: 2 sites, this module only

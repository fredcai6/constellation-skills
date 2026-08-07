# scripts.query_episodes:neighbours
function, scripts/query_episodes.py:368, 23 lines

```python
def neighbours(root: Path, episode_id: str, include_retired: bool = False) -> list
```

Every OTHER episode sharing at least one exact join key with `episode_id`.

Complete by construction (a union over all of JOIN_KEYS), unranked (id-sorted for
determinism only — a neighbour joined on two keys does not sort above one joined on
one; counting shared keys would be scoring, which section 8 forbids), and self
excluded. An unknown episode id raises rather than returning an empty
neighbourhood: "this episode has no neighbours" and "there is no such episode" are
different answers.

The NEIGHBOURHOOD is the ordinary set unless `include_retired` asks otherwise; the
ANCHOR is fetched by id, so an already-retired episode's surviving neighbours are
still reachable — which is what #308's consolidation pass needs in order to walk back
from an archived member of a cluster.

calls internal: _join_key_values x2, EpisodeNotFound, enumerate_episodes, fetch_episode
unresolved: 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only

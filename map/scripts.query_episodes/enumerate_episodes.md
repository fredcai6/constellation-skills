# scripts.query_episodes:enumerate_episodes
function, scripts/query_episodes.py:205, 23 lines

```python
def enumerate_episodes(root: Path, include_retired: bool = False) -> list
```

Every episode in the ordinary set as parsed records, id-sorted — or the

history-inclusive set when asked. The candidate set every other scanning primitive is
built from.

An id that the scan returned but fetch cannot resolve RAISES. It is the same rule as
the composition check above, one layer out: an earlier version dropped such an id with
an `if ep is not None`, which is a candidate set getting quietly shorter between two
lines of the same function — exactly the outcome this module exists to refuse. The
condition means the store changed underneath the scan, or the enumeration and
resolution seams disagree; both are facts a caller needs, and neither is "no match".

calls internal: QueryError, enumerate_episode_ids, fetch_episode
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only

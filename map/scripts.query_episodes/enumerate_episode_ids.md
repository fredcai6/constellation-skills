# scripts.query_episodes:enumerate_episode_ids
function, scripts/query_episodes.py:177, 26 lines

```python
def enumerate_episode_ids(root: Path, include_retired: bool = False) -> list[str]
```

Every episode id in the ordinary rhyme-search set, id-sorted for determinism.

Pass `include_retired=True` for the history-inclusive set — the archive is reached
deliberately or not at all.

Ordinary enumeration follows section 7's composition rule exactly: scan through the
iter_episode_ids() seam, then confirm each returned id through the
is_episode_in_ordinary_search() seam. Both steps, always, and a disagreement between
them raises rather than silently shortening the answer.

History-inclusive enumeration is the union of both sets and takes NO membership
filter — filtering here would re-exclude exactly what the caller asked to see, which
is the "forgot the union" trap arriving from the other direction.

calls internal: writer x2, HalfRetiredStore
calls stdlib: builtins.sorted
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

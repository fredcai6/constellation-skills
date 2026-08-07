# scripts.apply_episode_delta:_reject_half_retired
function, scripts/apply_episode_delta.py:646, 21 lines

```python
def _reject_half_retired(live: set[str], archived: set[str]) -> None
```

An id present in BOTH directories is a retirement that half-happened: retired by

content, still in the ordinary-search set by directory.

_Transaction.commit() compensates for every failure the process survives to observe,
so this state cannot be produced by a failed retirement — but a hard kill or power
loss between the two placement steps runs no compensation at all, and
markdown-in-git provides no journal to close that. Rather than claim the residue is
impossible, this makes it LOUD: an ordinary enumeration would otherwise return the
id and its record would read `status: retired`, which is a wrong answer with nothing
signalling it.

calls internal: EpisodeDeltaError
calls stdlib: builtins.sorted
reads internal: ACTIVE_DIR x2, RETIRED_DIR x2
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

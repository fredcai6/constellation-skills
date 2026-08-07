# tests.test_episode_store:naive_neighbours_first_key_wins
function, tests/test_episode_store.py:1090, 21 lines

```python
def naive_neighbours_first_key_wins(query_module, root, episode_id)
```

A NAIVE neighbour enumeration: try each join key in turn and return as soon as

one of them yields anything.

It reads perfectly reasonably — "find the episodes that share an artifact, and if
none do, fall back to the ones from the same role and step" — and it silently omits
every neighbour joined on a LATER key whenever an earlier key matched anything at
all. The candidate set handed to the downstream sensor is short, and nothing says
so. The real primitive takes the UNION over every join key.

calls stdlib: builtins.set x2, builtins.sorted x2
unresolved: 2 calls (dispatch-unknown-base), 9 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

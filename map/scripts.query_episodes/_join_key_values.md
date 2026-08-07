# scripts.query_episodes:_join_key_values
function, scripts/query_episodes.py:359, 7 lines

```python
def _join_key_values(episode) -> set[tuple[str, str]]
```

An episode's join-key values as (key-name, value) pairs. Two episodes are

neighbours exactly when these sets intersect — one set operation, so no join key
can be skipped, short-circuited, or ordered ahead of another.

calls internal: field_values
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only

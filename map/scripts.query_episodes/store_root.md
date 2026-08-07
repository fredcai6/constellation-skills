# scripts.query_episodes:store_root
function, scripts/query_episodes.py:136, 5 lines

```python
def store_root() -> Path
```

The store-root seam (EPISODE_STORE.md section 1), re-exported from the writer so

retrieval and writing can never disagree about where the store is. Deliberately NOT
durable_root().

calls internal: writer
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

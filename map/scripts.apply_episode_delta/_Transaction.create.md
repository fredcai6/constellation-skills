# scripts.apply_episode_delta:_Transaction.create
method, scripts/apply_episode_delta.py:1036, 4 lines

```python
def create(self, ep: Episode) -> None
```

HOLE: no docstring

calls internal: _Transaction.known_ids, _new_episode_path
reads internal: Episode.episode_id x4, _Transaction.loaded, _Transaction.original_paths, _Transaction.root
writes internal: _Transaction.loaded[], _Transaction.original_paths[]
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

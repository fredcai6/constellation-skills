# scripts.apply_episode_delta:_Transaction.load
method, scripts/apply_episode_delta.py:1025, 10 lines

```python
def load(self, episode_id: str) -> Episode
```

HOLE: no docstring

calls internal: EpisodeDeltaError, parse_episode, read_text_exact, resolve_episode_path
reads internal: _Transaction.loaded x3, _Transaction.original_paths, _Transaction.root
writes internal: _Transaction.loaded[], _Transaction.original_paths[]

referenced by: 2 sites, this module only

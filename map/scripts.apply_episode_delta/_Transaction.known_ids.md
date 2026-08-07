# scripts.apply_episode_delta:_Transaction.known_ids
method, scripts/apply_episode_delta.py:1020, 4 lines

```python
def known_ids(self) -> set[str]
```

HOLE: no docstring

calls internal: iter_episode_ids
calls stdlib: builtins.set
reads internal: _Transaction._known_ids x2, _Transaction.root
writes internal: _Transaction._known_ids

referenced by: 4 sites, this module only

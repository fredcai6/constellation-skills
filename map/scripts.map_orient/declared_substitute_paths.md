# scripts.map_orient:declared_substitute_paths
function, scripts/map_orient.py:711, 17 lines

```python
def declared_substitute_paths(receipt: dict) -> list[str]
```

PURE. Normalized paths of every substitute the receipt hash-pinned.

Only PINNED entries count: an entry with no real sha256 was never proven
read, so citing it in the frame proves nothing either.

calls internal: is_content_hash, is_filler, normalize_cited_path
calls stdlib: builtins.isinstance x3
reads stdlib: builtins.dict, builtins.list, builtins.str
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

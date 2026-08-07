# scripts.map_orient:map_inventory
function, scripts/map_orient.py:1093, 20 lines

```python
def map_inventory(root: Path, entrypoint: str | None) -> tuple[str, ...]
```

Impure edge: every anchor id the resolved entrypoint actually carries.

Recomputed from the map rather than read out of the receipt on purpose --
the receipt records a COUNT, and a count cannot answer set membership.

calls internal: _read_text x2, scan_anchors
calls stdlib: builtins.sorted, builtins.tuple
reads stdlib: builtins.str x2, builtins.dict, builtins.list
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

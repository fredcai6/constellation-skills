# scripts.docent_freshness:compute_stamp
function, scripts/docent_freshness.py:94, 10 lines

```python
def compute_stamp(map_root: Path) -> str
```

Return the canonical SHA-256 digest over the sorted source-map file set.

calls internal: _file_sha256, _iter_source_files
calls stdlib: hashlib.sha256, pathlib.Path
reads stdlib: builtins.list, builtins.str, hashlib (module)
writes internal: compute_stamp.map_root
unresolved: 7 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

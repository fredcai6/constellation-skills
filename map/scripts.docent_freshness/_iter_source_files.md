# scripts.docent_freshness:_iter_source_files
function, scripts/docent_freshness.py:67, 17 lines

```python
def _iter_source_files(map_root: Path) -> Iterable[Path]
```

Yield the source-map files that define the digest, in no particular order.

Deterministic ordering is imposed later by sorting on the relative path, so
the traversal order here does not matter.

unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

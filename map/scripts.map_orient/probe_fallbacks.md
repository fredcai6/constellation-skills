# scripts.map_orient:probe_fallbacks
function, scripts/map_orient.py:1115, 18 lines

```python
def probe_fallbacks(root: Path) -> list[dict]
```

Impure edge: which of the FIXED fallback set actually exist on disk.

This is the independent half of the degraded record -- existence is settled
by the filesystem, not by the agent's account of what it read.

calls internal: sha256_of
reads internal: KNOWN_FALLBACKS
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

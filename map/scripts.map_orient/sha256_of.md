# scripts.map_orient:sha256_of
function, scripts/map_orient.py:998, 6 lines

```python
def sha256_of(path: Path) -> str | None
```

Content hash used to pin a substitute; None when unreadable.

calls stdlib: hashlib.sha256
reads stdlib: builtins.OSError, hashlib (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

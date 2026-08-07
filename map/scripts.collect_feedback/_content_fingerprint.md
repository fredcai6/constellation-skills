# scripts.collect_feedback:_content_fingerprint
function, scripts/collect_feedback.py:196, 10 lines

```python
def _content_fingerprint(entry: dict[str, str]) -> str
```

Legacy fingerprint: hash of normalized observed+proposal prose.

Kept for backward-compatible sidecar lookups (entries collected/resolved
under the old scheme) and as the fallback when an entry has no candidate slug.

calls internal: _hash12
calls stdlib: re.sub x2
reads stdlib: re (module) x2
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

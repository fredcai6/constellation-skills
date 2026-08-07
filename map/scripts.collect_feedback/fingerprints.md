# scripts.collect_feedback:fingerprints
function, scripts/collect_feedback.py:243, 24 lines

```python
def fingerprints(entry: dict[str, str]) -> list[str]
```

Every key an entry may be recorded under, newest scheme first.

Includes the lesson-id fingerprint, the annotation-stripped slug fingerprint,
the prior raw-slug fingerprint (pre-stripping), and the legacy content hash —
so collected/resolved/filed state recorded under ANY earlier scheme still
matches after an identity change.

- [add](fingerprints.add.md) method: HOLE: no docstring

calls internal: _hash12 x3, _slugify x3, _raw_slug x2, _content_fingerprint
reads stdlib: builtins.str x2, builtins.list
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

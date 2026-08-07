# scripts.collect_feedback:fingerprint
function, scripts/collect_feedback.py:224, 17 lines

```python
def fingerprint(entry: dict[str, str]) -> str
```

Stable identity for a finding, in order of preference.

1. the originating lesson id (`Lesson` field) — the identity the lessons
   playbook curates and keeps stable across rewording via `amend`;
2. the candidate slug with annotations stripped — the fallback when an entry
   has no lesson id;
3. the legacy observed+proposal content hash — last resort.
Always 12 hex chars so the sidecar/ledger shape is unchanged.

calls internal: _hash12 x2, _slugify x2, _content_fingerprint
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

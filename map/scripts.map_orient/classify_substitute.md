# scripts.map_orient:classify_substitute
function, scripts/map_orient.py:691, 11 lines

```python
def classify_substitute(rel_path: str, exists: bool) -> str
```

PURE. Which oracle backs this substitute.

`known-fallback` requires BOTH corpus membership and filesystem presence --
membership alone would let a declared-but-absent `README.md` wear the
verified label, which is the self-attestation this labelling exists to
separate out.

calls internal: normalize_cited_path
reads internal: KNOWN_FALLBACK_SET, LABEL_AGENT_DECLARED, LABEL_KNOWN_FALLBACK

referenced by: 4 sites, this module only

# scripts.map_orient:pin_substitutes
function, scripts/map_orient.py:1142, 27 lines

```python
def pin_substitutes(root: Path, substitutes: Sequence[str]) -> list[dict]
```

Hash-pin each declared substitute so a later frame check has a prior.

An unreadable or nonexistent path gets `content_hash: null`, NOT a
sentinel string. A sentinel would satisfy a "is it non-empty" test and let
a mistyped path discharge the whole contract.

Each entry also carries `source`, the provenance label: `known-fallback`
when the path is in the fixed corpus set AND present on disk (the
filesystem, an oracle the agent does not author, agrees), `agent-declared`
otherwise. The label is a provenance NOTE, never a discharge -- an absent
substitute still refuses whatever it is called, which is why the label is
computed alongside the pin rather than in place of it.

calls internal: _rel, classify_substitute, sha256_of
calls stdlib: pathlib.Path x2
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

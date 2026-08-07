# scripts.curate_corpus:check_duplication
function, scripts/curate_corpus.py:314, 31 lines

```python
def check_duplication(bodies: dict[str, str]) -> list[Finding]
```

Corpus-level: report k-word shingles shared across >= MIN_CLUSTER_SKILLS

distinct skills. Grouped by the exact set of sharing skills so the human
table shows one row per shared-signature pattern, not one per shingle.

calls internal: Finding, _words
calls stdlib: builtins.len x5, builtins.sorted x4, builtins.set x2, builtins.frozenset, builtins.range
reads internal: SHINGLE_SIZE x3, Finding, MIN_CLUSTER_SKILLS, STATUS_FLAGGED
reads stdlib: builtins.str x5, builtins.dict x2, builtins.list x2, builtins.set x2, builtins.frozenset, builtins.len
unresolved: 11 calls (dispatch-unknown-base), 2 reads (unbound-name)

referenced by: 1 sites, this module only

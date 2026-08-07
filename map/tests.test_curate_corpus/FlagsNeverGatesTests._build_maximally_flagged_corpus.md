# tests.test_curate_corpus:FlagsNeverGatesTests._build_maximally_flagged_corpus
method, tests/test_curate_corpus.py:356, 23 lines

```python
def _build_maximally_flagged_corpus(self, root: Path)
```

Every detector firing at once in one corpus.

calls internal: write_skill x5, clean_frontmatter x4, write_raw_skill
calls stdlib: builtins.range
reads internal: COMPLIANCE_BOILERPLATE x2, cc x2
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

# scripts.curate_corpus:render_table
function, scripts/curate_corpus.py:385, 19 lines

```python
def render_table(findings: list[Finding]) -> str
```

A readable fixed-width findings table: skill | check | status | detail.

calls stdlib: builtins.len x2, builtins.sum x2, builtins.max, builtins.range, builtins.sorted
reads internal: STATUS_FLAGGED, STATUS_SHORTLIST
unresolved: 9 calls (dispatch-unknown-base), 9 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

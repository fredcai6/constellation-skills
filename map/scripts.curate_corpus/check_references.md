# scripts.curate_corpus:check_references
function, scripts/curate_corpus.py:292, 20 lines

```python
def check_references(skill: str, skill_dir: Path) -> list[Finding]
```

Each references/*.md longer than the threshold should carry a TOC heading.

calls internal: Finding x2
calls stdlib: builtins.len, builtins.sorted
reads internal: REFERENCE_TOC_LINE_THRESHOLD x2, STATUS_FLAGGED x2, Finding, TOC_MARKER_RE
reads stdlib: builtins.OSError, builtins.list
unresolved: 7 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

# scripts.curate_corpus:curate
function, scripts/curate_corpus.py:356, 27 lines

```python
def curate(root: Path) -> list[Finding]
```

Run every mechanical check over `root` (a skills/ directory) and return

all findings. Never raises for a bad skill — an unparseable skill becomes a
parse findings row and is excluded from the duplication corpus.

calls internal: CorpusParseError, Finding, _skill_dirs, check_description, check_duplication, check_invoker, check_references, check_size, parse_frontmatter
calls stdlib: builtins.str
reads internal: CorpusParseError, Finding, STATUS_FLAGGED
reads stdlib: builtins.str x2, builtins.OSError, builtins.dict, builtins.list
unresolved: 8 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

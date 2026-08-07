# scripts.curate_corpus:parse_frontmatter
function, scripts/curate_corpus.py:154, 28 lines

```python
def parse_frontmatter(text: str) -> tuple[dict[str, str], str]
```

Parse a leading YAML frontmatter block into a flat dict of top-level

scalar `key: value` pairs, returning (meta, body). Raises CorpusParseError
on missing or unterminated frontmatter — the caller turns that into a row.

Deliberately minimal (stdlib-only, no yaml dep): the corpus frontmatter is
flat single-line scalars. Block scalars / nested maps are not expected; a
key we cannot parse is simply skipped, not fatally malformed.

calls internal: CorpusParseError x2
calls stdlib: builtins.len, builtins.range, re.match
reads stdlib: builtins.str x2, builtins.dict, re (module)
unresolved: 10 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

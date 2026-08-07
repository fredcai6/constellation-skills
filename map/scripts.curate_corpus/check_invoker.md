# scripts.curate_corpus:check_invoker
function, scripts/curate_corpus.py:280, 10 lines

```python
def check_invoker(skill: str, meta: dict[str, str]) -> list[Finding]
```

Presence + validity of the `invoker:` frontmatter tag.

calls internal: Finding x3
reads internal: STATUS_FLAGGED x2, VALID_INVOKERS x2, STATUS_OK
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

# scripts.collect_feedback:_is_finding
function, scripts/collect_feedback.py:169, 7 lines

```python
def _is_finding(entry: dict[str, str]) -> bool
```

A parsed block is a real finding only if it carries at least one substantive

field. Section headers and malformed blocks (no candidate, observed, or
proposal) are export noise — they otherwise hash-collide on empty content into
bogus "recurring" candidates. Same spirit as the `<date>` placeholder skip.

calls stdlib: builtins.any
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

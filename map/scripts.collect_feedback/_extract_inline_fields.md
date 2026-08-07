# scripts.collect_feedback:_extract_inline_fields
function, scripts/collect_feedback.py:79, 17 lines

```python
def _extract_inline_fields(body: str) -> tuple[dict[str, str], str]
```

Pull `**Label:** value` spans out of a prose sub-block.

Returns (fields, leading_prose) where leading_prose is the text before the
first label (used as `observed` when no explicit **Observed:** is present).

calls stdlib: builtins.len x2, builtins.enumerate, builtins.list
reads internal: INLINE_FIELD_RE
reads stdlib: builtins.str x2, builtins.dict
unresolved: 12 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

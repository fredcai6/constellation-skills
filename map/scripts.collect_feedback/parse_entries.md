# scripts.collect_feedback:parse_entries
function, scripts/collect_feedback.py:119, 16 lines

```python
def parse_entries(text: str) -> list[dict[str, str]]
```

HOLE: no docstring

calls stdlib: builtins.len x2, builtins.enumerate, builtins.list
reads internal: ENTRY_HEADING_RE, FIELD_RE
reads stdlib: builtins.str x2, builtins.dict, builtins.list
unresolved: 16 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

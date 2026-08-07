# scripts.map_orient:scan_anchors
function, scripts/map_orient.py:289, 12 lines

```python
def scan_anchors(text: str) -> list[str]
```

PURE. Unique citable anchor ids in `text`, in first-seen order.

Format-agnostic on purpose: it reads YAML-fenced packets, bold-field
packets, generated JSON, and free prose identically. A `<placeholder>`
cannot match -- `<` is outside the id character class -- so an unfilled
template scaffold yields the empty list.

calls stdlib: builtins.list
reads internal: ANCHOR_RE
reads stdlib: builtins.dict, builtins.str
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 11 sites, this module only

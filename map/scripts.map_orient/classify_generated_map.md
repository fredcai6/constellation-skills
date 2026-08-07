# scripts.map_orient:classify_generated_map
function, scripts/map_orient.py:387, 22 lines

```python
def classify_generated_map(text: str) -> tuple[bool, list[str], str]
```

PURE. (has_content, anchors, note) for a `generated/map.json` candidate.

calls internal: scan_anchors
calls stdlib: builtins.isinstance x4, builtins.len x3, json.loads
reads stdlib: builtins.dict x2, builtins.ValueError, builtins.list, builtins.str, json (module)
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 6 sites, this module only

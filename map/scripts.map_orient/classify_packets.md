# scripts.map_orient:classify_packets
function, scripts/map_orient.py:421, 13 lines

```python
def classify_packets(packet_texts: dict[str, str]) -> tuple[bool, list[str], str]
```

PURE. (has_content, anchors, note) for the `packets/*.md` candidate.

calls internal: scan_anchors
calls stdlib: builtins.len x4, builtins.list, builtins.sorted
reads stdlib: builtins.dict, builtins.str
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 4 sites, this module only

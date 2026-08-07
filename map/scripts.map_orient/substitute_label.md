# scripts.map_orient:substitute_label
function, scripts/map_orient.py:704, 5 lines

```python
def substitute_label(entry: object) -> str
```

PURE. The label on a receipt substitute; unlabelled reads as unverified.

calls stdlib: builtins.isinstance
reads internal: LABEL_AGENT_DECLARED, SUBSTITUTE_LABELS
reads stdlib: builtins.dict
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 4 sites, this module only

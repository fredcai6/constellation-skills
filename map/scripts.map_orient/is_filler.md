# scripts.map_orient:is_filler
function, scripts/map_orient.py:460, 10 lines

```python
def is_filler(value: object) -> bool
```

PURE. True when a field is absent, empty, a placeholder, or says nothing.

calls stdlib: builtins.isinstance
reads internal: FILLER_VALUES
reads stdlib: builtins.str
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 5 sites, this module only

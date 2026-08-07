# scripts.map_orient:substitute_problems
function, scripts/map_orient.py:485, 21 lines

```python
def substitute_problems(receipt: dict) -> list[str]
```

PURE. Why the declared substitutes fail to pin; empty means they pin.

calls internal: is_content_hash, is_filler
calls stdlib: builtins.isinstance x2, builtins.enumerate
reads stdlib: builtins.dict, builtins.list
unresolved: 9 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

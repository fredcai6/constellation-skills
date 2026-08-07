# scripts.map_orient:substitutes_declared
function, scripts/map_orient.py:508, 13 lines

```python
def substitutes_declared(receipt: dict) -> bool
```

PURE. >=1 substitute, each with a real path AND a real sha256 pin.

An empty `substitutes` list is a refusal, not a pass: a degraded run read
SOMETHING instead of the map, and the hash pins it so a later frame check
compares against this prior declaration rather than a same-breath claim.

A substitute that could not be read is likewise a refusal. Emitting a
sentinel there and accepting it would let a single typo -- a path that does
not exist -- discharge the whole contract at exit 0, which is precisely the
hole this module exists to close.

calls internal: substitute_problems

referenced by: 7 sites, this module only

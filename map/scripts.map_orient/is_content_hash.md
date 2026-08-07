# scripts.map_orient:is_content_hash
function, scripts/map_orient.py:472, 11 lines

```python
def is_content_hash(value: object) -> bool
```

PURE. True only for a real sha256 hex digest.

Checking the SHAPE, not merely "is it non-empty", is what stops a sentinel,
a typo, or a truncated digest from passing as a hash-pin. A substitute that
could not be read has NO hash, and a record that cannot pin what it read
has not discharged anything.

calls stdlib: builtins.isinstance
reads internal: CONTENT_HASH_RE
reads stdlib: builtins.str
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 4 sites, this module only

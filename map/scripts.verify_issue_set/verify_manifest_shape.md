# scripts.verify_issue_set:verify_manifest_shape
function, scripts/verify_issue_set.py:58, 24 lines

```python
def verify_manifest_shape(manifest: object) -> dict
```

Structural basics of the one manifest: an epic with a title and a

non-empty list of issues, each with a unique id and a title.

calls internal: _require x8
calls stdlib: builtins.isinstance x7, builtins.bool x3, builtins.str x3, builtins.enumerate, builtins.len, builtins.set
reads stdlib: builtins.dict x5, builtins.list x2, builtins.set, builtins.str
unresolved: 9 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

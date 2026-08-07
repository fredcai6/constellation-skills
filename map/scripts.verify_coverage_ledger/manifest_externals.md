# scripts.verify_coverage_ledger:manifest_externals
function, scripts/verify_coverage_ledger.py:39, 6 lines

```python
def manifest_externals(manifest: dict) -> list[str]
```

Flatten every installed external skill name across all sources.

reads stdlib: builtins.list, builtins.str
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

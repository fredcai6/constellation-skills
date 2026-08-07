# scripts.verify_coverage_ledger:verify_coverage_ledger
function, scripts/verify_coverage_ledger.py:52, 46 lines

```python
def verify_coverage_ledger(ledger: dict, manifest: dict, skills_root: Path) -> None
```

Raise CoverageLedgerError on the first rail violation; return None if clean.

calls internal: CoverageLedgerError x2, manifest_externals, skill_exists
calls stdlib: builtins.set x2, builtins.sorted x2, builtins.isinstance, builtins.str
reads internal: _VALID_STATUS x2
reads stdlib: builtins.list x2, builtins.str x2, builtins.set
unresolved: 14 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

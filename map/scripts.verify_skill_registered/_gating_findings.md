# scripts.verify_skill_registered:_gating_findings
function, scripts/verify_skill_registered.py:64, 10 lines

```python
def _gating_findings(skill: str, root: Path) -> list[str]
```

Run curate's mechanical checks over `root` and return the details of every

FLAGGED finding for `skill` that falls in the mint-blocking GATING subset.

calls third-party: curate_corpus.curate
reads internal: GATING_CHECKS
reads stdlib: builtins.list, builtins.str
reads third-party: curate_corpus (module) x2, curate_corpus.STATUS_FLAGGED
unresolved: 1 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

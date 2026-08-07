# scripts.run_skill_eval:_dry_run_engine_spine
function, scripts/run_skill_eval.py:799, 62 lines

```python
def _dry_run_engine_spine() -> dict
```

A minimal ENGINE-SHAPED terminal spine for the dry-run smoke: the gated

`tasks` form with every task complete, a plausible `engine_session` lease
(monotonic claim -> heartbeat -> release), and one engine-produced
`command-output` evidence item backing its command postcondition. Since #127
hardened `spine_completed` to demand engine provenance (a bare
`{"status": "done"}` no longer passes), the runner's own falsification-floor
smoke must synthesize the same engine fingerprints a real driven spine leaves —
otherwise the dry-run would fail the very check it exists to exercise.

calls stdlib: datetime.timedelta x2, datetime.datetime.now
reads stdlib: datetime.datetime, datetime.timezone, datetime.timezone.utc
unresolved: 1 calls (dispatch-unknown-base), 1 reads (unbound-name)

referenced by: 1 sites, this module only

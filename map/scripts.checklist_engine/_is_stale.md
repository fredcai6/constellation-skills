# scripts.checklist_engine:_is_stale
function, scripts/checklist_engine.py:840, 16 lines

```python
def _is_stale(session: dict | None, config: dict) -> bool
```

A lease is stale when its `last_heartbeat` is older than the configured

timeout. A missing/closed lease, or one with an unparseable heartbeat, is
treated conservatively (a missing one is not 'stale'; it just isn't active).
Tests can drive staleness by writing an old `last_heartbeat` directly, or by
monkeypatching `_now`.

calls internal: _parse_ts x2, _now, lease_stale_seconds
reads stdlib: builtins.TypeError, builtins.ValueError
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only

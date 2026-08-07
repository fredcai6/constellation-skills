# scripts.checklist_engine:_refresh_owner_heartbeat
function, scripts/checklist_engine.py:867, 12 lines

```python
def _refresh_owner_heartbeat(cl: dict, session_id: str | None) -> None
```

Stamp liveness: if `session_id` owns the active lease, advance its

`last_heartbeat` to now. No-op when there is no active lease, a different
session owns it, or `session_id` is falsy. Called after every mutating verb
the owner issues *and that succeeds*, so an actively-working owner never goes
stale and a genuine idle gap self-heals on the owner's next successful verb.
A refused verb never reaches here, so a failing-only session can still go
stale. It never writes a takeover record — the owner resuming its own work is
not a takeover.

calls internal: _active_lease, _now
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

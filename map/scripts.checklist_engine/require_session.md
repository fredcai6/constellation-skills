# scripts.checklist_engine:require_session
function, scripts/checklist_engine.py:881, 29 lines

```python
def require_session(cl: dict, verb: str, session_id: str | None, config: dict) -> None
```

The actor-authority gate. Mutating verbs are session-gated only ONCE an

ACTIVE lease exists; with no active lease a missing `--session-id` is fine
(legacy checklists/templates have no `engine_session`).

Staleness gates **non-owners only** — it answers "has the owner gone quiet
long enough that someone else may seize the lease?" The rightful owner is
NEVER blocked by its own staleness, because an owner issuing a verb IS the
liveness signal (the stamp `_refresh_owner_heartbeat` records it). So the
owner always passes; a non-owner is refused — with a `claim` instruction if
the lease is stale, or an ownership instruction if it is a different,
still-active lease.

calls internal: EngineError x2, _active_lease, _is_stale
reads internal: MUTATING_VERBS
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

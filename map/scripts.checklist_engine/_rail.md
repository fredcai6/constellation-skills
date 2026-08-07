# scripts.checklist_engine:_rail
function, scripts/checklist_engine.py:269, 29 lines

```python
def _rail(point: str, cl: dict) -> str
```

Return the doctrine block to append at a decision point, or ``""`` when no

rail applies. Non-gated (survey) checklists get NO rail. ``point`` is either
``"check-failure"`` (the REFUSED path, no token substitution) or any railed verb
name, in which case the position is derived from ``items`` state.

Issue #420: on the `current` verb specifically, `render_human()`'s own
``ACTIVE {id} [{status}] — {imperative}`` line already prints the active
gate's full imperative, so substituting it AGAIN into the mid-flight rail's
``{imperative}`` token duplicated it. For every OTHER railed verb
(claim/start/advance/attest/attach) there is no ACTIVE line in that verb's
own output — the rail's imperative mention is the ONLY place the caller
sees "what's next" there, so it must keep the full text unchanged. The fix
is verb-aware and touches only what fills the token, never the frozen
`_RAIL_STRINGS` values themselves: substitute a short pointer for
`{imperative}` only when `point == "current"` and the position is
`mid-flight` (the only position that uses the `{imperative}` token).

calls internal: _rail_position
calls stdlib: builtins.dict, builtins.str
reads internal: _RAIL_STRINGS x2, GATED, _RAIL_CURRENT_MIDFLIGHT_POINTER
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

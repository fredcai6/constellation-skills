# scripts.checklist_engine:has_pending_refresh_request
function, scripts/checklist_engine.py:1107, 31 lines

```python
def has_pending_refresh_request(cl: dict, gate: str, why_ref: str | None = None) -> bool
```

Pure predicate: True iff a pending `refresh-request` targets `gate`.

A refresh-request is a `refresh-request`-typed evidence item (attached via the
ordinary `attach` verb) whose payload carries POINTERS ONLY: `seam` = the gate
it concerns, `why_ref` = the why-record id it was raised against — never copies
of state. It is pending while present and not superseded (the reopen cascade
supersedes evidence; the flow that consumes/fulfils it is #183). No shared
mutable state, no side effects.

`why_ref` (#190) is an OPTIONAL identity filter. When None (the default — the
DISPLAY semantic: "a refresh is pending for this gate"), any pending request for
the gate matches, UNCHANGED. When given, a pending request ALSO has to carry the
matching `payload.why_ref` — an identity match, so a NEW trip on a still-open
gate cannot ride a stale/earlier request's coattails (HARD-band callers pass the
current-digest why-record id; a None id degrades to the gate-only match).

calls stdlib: builtins.isinstance x2
reads stdlib: builtins.dict x2
unresolved: 8 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only

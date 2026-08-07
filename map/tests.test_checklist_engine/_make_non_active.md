# tests.test_checklist_engine:_make_non_active
function, tests/test_checklist_engine.py:71, 25 lines

```python
def _make_non_active(cl, active_status='pending', active_status_detail=None)
```

Given a single-item GATED checklist built via `gated(g1=...)`, return

an equivalent checklist with the SAME target task ('g1'), preceded by a
dummy guard gate ('g0', status `active_status`) so g1 is guaranteed
NON-active. This is the shape `recovery_for`'s active-gate-position
branch needs and which no single-task fixture (used by every
recovery-family test before rework 2) can ever express (Reviewer BLOCK,
g3-review rework 2).

`active_status` defaults to `"pending"`, matching every caller before
rework 3->4 -- but a hardcoded `"pending"` guard could only ever express
the ONE case where `start()`'s own bare "not the active gate; start
{active} first" message happens to be self-recovering (Finding 1,
g3-review rework 3->4): it could never express `in-progress` or
`blocked`, exactly the two states where that unconditional advice
itself refuses. Pass `active_status="in-progress"` / `"blocked"` to
express those. `active_status_detail` optionally sets the guard gate's
own `status_detail` (e.g. a `blocked` guard's restorability).

calls internal: gate
calls stdlib: copy.deepcopy
reads stdlib: copy (module)
unresolved: 1 writes (non-name-expr)

referenced by: 9 sites, this module only

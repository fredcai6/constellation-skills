# scripts.checklist_engine:_next_verbs
function, scripts/checklist_engine.py:1505, 58 lines

```python
def _next_verbs(aid: str, t: dict, kind: str) -> list[str]
```

Legal-from-here move templates for the active task, hand-derived from

the RUNTIME contract of each verb's body — NOT from argparse. Two traps
this must not reintroduce:

INV-1 (g2 handoff): `advance --why` is optional at `parse_args()` but
required at runtime unless `--mechanical` or the gate is `why_exempt` (see
`advance()`); `attest --evidence` is optional at `parse_args()` but
required at runtime whenever the condition's `check.kind == "artifact"`
(see `attest()`). Walking `parser._actions` for `required=True` would
silently omit exactly those two.

Rework 1 (g2 review BLOCK): the TERMINAL verb (`start` for a pending task,
`advance` for an in-progress one) must only appear once every blocking
null/artifact condition for it is resolved — see `_blocking_conditions()`.
The gate is ASYMMETRIC: `start()` refuses on unmet PREconditions, `advance()`
on unmet POSTconditions, so each is checked against its own list only.
`resume`/`record` carry no precondition/postcondition gate at all (see
`resume()`/`record()`), so they are never suppressed.

Placeholders (`<...>`) mark free text only the agent can supply; every
other token is a real id read off THIS task.

calls internal: _blocking_conditions x2, _attestable, _condition_kind, _condition_open
reads internal: SURVEY
reads stdlib: builtins.list, builtins.str
unresolved: 11 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

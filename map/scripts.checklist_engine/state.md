# scripts.checklist_engine:state
function, scripts/checklist_engine.py:1565, 44 lines

```python
def state(cl: dict) -> dict
```

Pure state projection: `cl -> StateView`. Read-only — see the INV-2

purity note above. `current()` is `render_human(state(cl))`; the whole
completeness upgrade (#227 items 1+3) lives here, not in the adapter.

calls internal: _condition_view x2, _lease_line, _next_verbs, _why_suffix, active_id, task
reads internal: GATED, SURVEY, _STATE_CONTRACT_VERSION
reads stdlib: builtins.list, builtins.str
unresolved: 12 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

# scripts.checklist_engine:dispatch
function, scripts/checklist_engine.py:2505, 50 lines

```python
def dispatch(cl: dict, args: argparse.Namespace, base_dir: Path | None = None) -> str
```

HOLE: no docstring

calls internal: _rail_prefix, _refresh_owner_heartbeat, _run_verb, _trip_advisory, _trip_hard_gate, claim, current, heartbeat, load_config, release, require_session
reads internal: MUTATING_VERBS, RAIL_VERBS
unresolved: 6 calls (dynamic), 6 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

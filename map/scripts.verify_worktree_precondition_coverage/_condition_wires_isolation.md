# scripts.verify_worktree_precondition_coverage:_condition_wires_isolation
function, scripts/verify_worktree_precondition_coverage.py:72, 12 lines

```python
def _condition_wires_isolation(cond: dict) -> bool
```

True if `cond` is a command check that runs verify_worktree_isolation.py

and is unmet by default (a shipped template must never pre-satisfy its own
check -- that would defeat the gate for every run instantiated from it).

calls stdlib: builtins.isinstance
reads internal: ISOLATION_SCRIPT_MARKER
reads stdlib: builtins.dict
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

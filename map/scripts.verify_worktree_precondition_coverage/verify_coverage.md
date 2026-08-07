# scripts.verify_worktree_precondition_coverage:verify_coverage
function, scripts/verify_worktree_precondition_coverage.py:94, 29 lines

```python
def verify_coverage(root: Path) -> int
```

Check every listed (template, gate) pair. Returns the count checked on

success; raises CoverageError naming every offending template/gate on
failure (never a bare "FAIL" -- see references/global-orchestrator.md,
"A check that cannot fail" -- state the count, name the gap).

calls internal: CoverageError, _gate_wires_isolation
calls stdlib: builtins.len, json.loads
reads internal: WORKTREE_ENTERING_GATES x2, ISOLATION_SCRIPT_MARKER
reads stdlib: json (module) x2, builtins.list, builtins.str, json.JSONDecodeError
unresolved: 9 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

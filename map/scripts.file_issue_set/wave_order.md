# scripts.file_issue_set:wave_order
function, scripts/file_issue_set.py:76, 21 lines

```python
def wave_order(manifest: dict) -> list[list[dict]]
```

Kahn-style layering: wave 0 = issues nothing blocks-into (no unmet

dependency), then peel. `A blocks B` means A must precede B. A cycle raises
(the rail already rejects dangling edges; a cycle is the remaining hazard).

calls stdlib: builtins.len x2, builtins.set x2, builtins.str
calls third-party: verify_issue_set.IssueSetError
reads stdlib: builtins.str x3, builtins.dict x2, builtins.list x2, builtins.set x2
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

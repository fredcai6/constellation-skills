# scripts.hooks.spine_rail:_foreign_worktree
function, scripts/hooks/spine_rail.py:325, 17 lines

```python
def _foreign_worktree(data: dict, b: dict) -> bool
```

True only when the stopping session's cwd is positively a DIFFERENT

worktree than the binding's recorded worktree.

Returns True iff both `data["cwd"]` and `b["worktree"]` are truthy AND
`_same_path` says they differ. Absent either -> False: no positive mismatch
evidence, so the rail does not relax (and `_same_path`'s fail-safe True keeps
an errored comparison from reading as foreign).

calls internal: _same_path
reads stdlib: builtins.Exception
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only

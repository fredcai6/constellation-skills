# scripts.verify_worktree_isolation:parse_worktree_list
function, scripts/verify_worktree_isolation.py:55, 9 lines

```python
def parse_worktree_list(porcelain: str) -> list[str]
```

The registered worktree paths from `git worktree list --porcelain` output.

Each record opens with a `worktree <path>` line; the `HEAD`, `branch`, `bare`,
`detached`, and blank lines that follow are ignored.

calls stdlib: builtins.len
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

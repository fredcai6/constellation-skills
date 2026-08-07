# scripts.apply_episode_delta:store_root
function, scripts/apply_episode_delta.py:505, 7 lines

```python
def store_root() -> Path
```

The ONE named seam for where episodes/ lives (EPISODE_STORE.md section 1): the

literal relative path from the repository root. Deliberately NOT durable_root() —
under an active Admiral epic lease durable_root() would redirect to the worktree
root and silo the store per worktree, which is exactly wrong for a tracked path
that is the same logical directory in every worktree the moment a commit lands.

calls stdlib: pathlib.Path
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base), 1 reads (unbound-name)

referenced by: 1 sites, this module only

# scripts.episode_capture:project_name
function, scripts/episode_capture.py:107, 40 lines

```python
def project_name(base_dir: Any = None) -> str | None
```

The `project` mechanical field: the REPOSITORY's name, identical from every

worktree — or `None`, refusing, when it cannot be sourced honestly.

Sourced from the parent of `git rev-parse --git-common-dir`, which is repository
*topology*: in a linked worktree it names the main checkout's `.git` regardless of
any lease, and in a plain checkout it is `.git`, whose parent is the checkout root.

**Deliberately NOT `durable_root()`, and the difference is not academic.** That
helper answers a *writability* question, and it returns the worktree unchanged
whenever an active Admiral epic lease exists (its own comment: "the main checkout
is fenced read-only, so honor the worktree") — which is the condition every
commander in an epic runs under. Sourcing `project` there gives the same repository
a different name every epic (`e298-305` rather than `constellation-skills`), which
is exactly the drift this field exists to prevent. Measured, not reasoned:
`durable_root()` in this repo's own epic worktree resolves to the worktree.

Refuses rather than guessing. `repo_root()` above may fall back to `base_dir`
because a manifest full of `rev: null` is a visible, truthful non-reading — but
there is no such visible failure here. A worktree-derived project name is a
*plausible* value that silently poisons the one join meant to survive
`git worktree remove`, and a fabricated mechanical fact is worse than an absent one.

calls stdlib: pathlib.Path x3, builtins.str x2, os.path.abspath x2, os.fspath, os.path.join, pathlib.Path.cwd, subprocess.run
reads stdlib: os (module) x4, os.path x3, builtins.OSError, pathlib.Path, subprocess (module)
unresolved: 1 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

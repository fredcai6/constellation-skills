# scripts.episode_capture:repo_root
function, scripts/episode_capture.py:79, 26 lines

```python
def repo_root(base_dir: Any = None) -> Path
```

The worktree root `repo`-rooted declarations resolve against.

`docs/agents/ORCHESTRATOR_CONTEXT.md` and its neighbours live here, so this must
be the worktree the run is happening in — not the main checkout, which is what
`durable_root` deliberately resolves to instead.

Any failure (no git on PATH, `base_dir` outside a repository, `base_dir` not a
directory) falls back to `base_dir` itself rather than raising or guessing. That
mirrors `agent_work_root.durable_root`'s own never-raise contract, and it keeps
the non-repository case a manifest full of `rev: null` rows — a visible,
truthful "these files were not there" — instead of a broken verb.

calls stdlib: pathlib.Path x3, os.path.abspath x2, builtins.str, os.fspath, pathlib.Path.cwd, subprocess.run
reads stdlib: os (module) x3, os.path x2, builtins.OSError, pathlib.Path, subprocess (module)
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

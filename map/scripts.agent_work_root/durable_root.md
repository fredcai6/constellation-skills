# scripts.agent_work_root:durable_root
function, scripts/agent_work_root.py:110, 32 lines

```python
def durable_root(start: str | os.PathLike[str] | None = None) -> Path
```

The durable checkout root for `.agent-work` resolution.

Returns the MAIN checkout root only when `start` sits inside a LINKED git
worktree. For a plain checkout, a non-git directory, or ANY git error, returns
`start` (or cwd) unchanged. Never raises.

calls internal: _git_rev_parse x2, _normalize x2, _active_epic_lease
calls stdlib: os.path.join x3, os.path.abspath x2, pathlib.Path x2, os.fspath, os.path.dirname, pathlib.Path.cwd
reads stdlib: os (module) x7, os.path x6, builtins.OSError, builtins.RuntimeError, pathlib.Path

referenced by: 2 sites, this module only

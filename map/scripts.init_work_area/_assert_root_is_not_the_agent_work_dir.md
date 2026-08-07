# scripts.init_work_area:_assert_root_is_not_the_agent_work_dir
function, scripts/init_work_area.py:54, 16 lines

```python
def _assert_root_is_not_the_agent_work_dir(root: Path) -> None
```

Refuse a ``--root`` that already ends in ``.agent-work``.

``--root`` is the *project/worktree* root; this script appends its own
``.agent-work`` segment. The flag name reads as "the agent-work root",
so passing the ``.agent-work`` directory itself is an easy slip — and it
silently scaffolds ``.agent-work/.agent-work/<work-id>/`` rather than
failing, leaving a run's artifacts one level below where every other
script (and ``durable_root()``) looks for them.

calls stdlib: builtins.SystemExit, builtins.str
unresolved: 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

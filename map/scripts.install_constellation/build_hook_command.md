# scripts.install_constellation:build_hook_command
function, scripts/install_constellation.py:771, 15 lines

```python
def build_hook_command(script_path: Path, interpreter: str) -> str
```

The literal `command` string an entry carries.

ABSOLUTE, and never `${CLAUDE_PROJECT_DIR}`. That variable delivers its
anti-tamper property only as an accident of undocumented harness behaviour
(#269 established it is fixed at session launch, so it HAPPENS to point at
the main checkout for an agent working in a worktree) -- unowned by us and
one release from changing. An absolute installed path is pinned BY
CONSTRUCTION and asks the harness to guarantee nothing, which is what
actually protects the ruling that an agent's own branch cannot edit the code
that judges it.

`interpreter` comes from the run's single `resolve_interpreter()` probe --
never re-probed here, never hardcoded.

unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only

# scripts.run_crew:build_crew_argv
function, scripts/run_crew.py:200, 20 lines

```python
def build_crew_argv(launcher: str, *, role: str, handoff: str, model: str | None, session: str) -> list[str]
```

PURE construction of the agent-CLI command line from role/handoff/model.

Kept separate so tests can assert on the argv without spawning anything. The
real launcher binary is configurable (`--command`) and defaults sensibly; the
handoff is passed by path (the wrapper has already refused a missing one).

The claude CLI has no `--session`/`--role`/`--handoff` flags (issue #91: the
old flag form fails with `unknown option '--session'` on current CLIs), so
role, session name, and handoff path travel inside the headless `-p` prompt;
the registry — not the CLI — owns crew identity.

reads stdlib: builtins.list, builtins.str

referenced by: 2 sites, this module only

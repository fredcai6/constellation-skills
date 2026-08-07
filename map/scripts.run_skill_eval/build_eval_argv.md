# scripts.run_skill_eval:build_eval_argv
function, scripts/run_skill_eval.py:265, 15 lines

```python
def build_eval_argv(launcher: str, *, prompt: str, model: str | None, permission_mode: str | None = None) -> list[str]
```

PURE construction of the headless agent command line. Exactly

`[launcher, "-p", prompt]`, plus `--model <model>` when a model is set,
`--permission-mode <mode>` when a mode is set, and the EXEC_ALLOWED_TOOLS
allowlist. Kept separate so tests assert on the argv without spawning
anything. The permission mode covers file writes (issue #115 tc2); the
allowed-tools list covers non-interactive python/pytest execution (#126).

reads internal: EXEC_ALLOWED_TOOLS

referenced by: 1 sites, this module only

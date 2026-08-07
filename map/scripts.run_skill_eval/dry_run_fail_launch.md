# scripts.run_skill_eval:dry_run_fail_launch
function, scripts/run_skill_eval.py:897, 13 lines

```python
def dry_run_fail_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout) -> LaunchOutcome
```

Fake launcher that synthesizes a BROKEN workspace (no completion artifact)

so the process checks catch it — the agent-free FALSIFICATION FLOOR. Exits 0
so the run is a COMPLETED-fail (tallied, exit 1), never fenced. Spawns
NOTHING.

calls internal: LaunchOutcome, _write_transcript
calls stdlib: json.dumps, pathlib.Path
reads stdlib: json (module)
unresolved: 3 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only

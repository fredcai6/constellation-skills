# scripts.run_crew:build_entry
function, scripts/run_crew.py:321, 56 lines

```python
def build_entry(*, work_id: str, gate: str, role: str, attempt: int, worktree: str, handoff: str, result: str, root: Path, started: str, backend: str, pid: int | None, dispatch: str | None = None, model: str | None = None) -> dict
```

Construct the base `crew-runs.json` entry shared by BOTH backends (the

consolidation the wave-1 triage named). One place builds the durable record so
the two dispatch paths can never drift in shape.

Every new entry carries a `backend` field (`"cli"` | `"external"`, Decision 1)
and starts `running` so the duplicate-guard/recovery classifier treat it as an
in-flight attempt. Backend-specific shape is passed in, not forked here:
  * `pid`      — the spawning process (cli) or `None` (external, PID-less).
  * `dispatch` — external keeps its legacy `dispatch: "external"` marker
                 (Decision 5) so today's tooling and records still parse;
                 the cli backend passes `None` (no marker, as before).
  * `model`    — recorded only when the caller stored it (external), matching
                 the prior per-path shape; the cli path does not store it.

calls internal: _relativize x4, run_log_paths, session_name
calls stdlib: builtins.str x2

referenced by: 2 sites, this module only

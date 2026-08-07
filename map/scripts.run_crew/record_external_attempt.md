# scripts.run_crew:record_external_attempt
function, scripts/run_crew.py:711, 31 lines

```python
def record_external_attempt(*, work_id: str, gate: str, role: str, handoff: str, result: str, worktree: str, model: str | None, attempt: int, root: Path, entries: list[dict]) -> dict
```

Record a durable crew-runs.json entry for an EXTERNALLY-dispatched crew

WITHOUT spawning a subprocess. Thin wrapper over `ExternalBackend.dispatch`
(signature + observable behavior preserved: returns the entry dict).

In the Agent-tool harness there is no headless `claude` CLI to spawn, so the
implementer/reviewer is dispatched out-of-band and only the wrapper's DURABLE
safety properties are wanted — a registry record, the duplicate-guard, and
result-artifact verification. The entry is marked `dispatch="external"` and is
PID-less (`pid=None`) so downstream tooling (recover_crews) can tell it apart
from a spawned crew; it starts `running` so the duplicate-guard/recovery
classifier treat it like an in-flight attempt until its result is verified
(see `verify_external_result`). Refuses if the handoff file is missing.

calls internal: CrewSpec, ExternalBackend
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

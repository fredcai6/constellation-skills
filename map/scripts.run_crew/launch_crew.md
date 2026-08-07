# scripts.run_crew:launch_crew
function, scripts/run_crew.py:656, 27 lines

```python
def launch_crew(*, work_id: str, gate: str, role: str, handoff: str, result: str, worktree: str, model: str | None, launcher: str, attempt: int, root: Path, entries: list[dict], launch: 'callable | None' = None) -> tuple[int, dict]
```

Record the durable entry BEFORE launching, run the crew foreground, then

finalize the entry from the child exit code + result-artifact freshness.

Thin wrapper over `CliBackend.dispatch` (signature + observable behavior
preserved). Returns (exit_code, entry). Refuses if the handoff file is missing.
`launch` defaults to the module-level `launch_process` resolved at CALL time,
so monkeypatching the seam (in tests) takes effect even through the CLI.

calls internal: CliBackend, CrewSpec
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found

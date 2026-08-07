# scripts.run_crew:resume_crew
function, scripts/run_crew.py:685, 24 lines

```python
def resume_crew(*, session: str, root: Path, entries: list[dict], launch: 'callable | None' = None) -> tuple[int, dict]
```

Continue a recorded crew using its STORED session name and handoff, routing

to the RECORDED entry's backend (Decision 6). `entry_backend(entry)` picks the
backend: a `cli` entry relaunches the subprocess and finalizes (today's
behavior); an `external` entry is unrecoverable-by-wrapper — `ExternalBackend`
raises `CrewLaunchError` with the SendMessage-to-agentId / --abandon --relaunch
guidance, so recovery NEVER silently spawns for an externally-dispatched crew.

An unknown session has no entry to route from, so it falls to `CliBackend`,
which raises the standard `cannot resume: no crew recorded` refusal (unchanged).
`launch` defaults to the module-level `launch_process` resolved at CALL time.

calls internal: CliBackend, CrewBackend.resume, ExternalBackend, entry_backend, find_entry
reads internal: BACKEND_EXTERNAL, CrewBackend

referenced by: 1 sites, this module only

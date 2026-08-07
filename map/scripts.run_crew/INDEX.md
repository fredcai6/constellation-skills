# scripts.run_crew
scripts/run_crew.py, 944 lines, 10 holes

Safe crew launcher with a durable session-recovery registry.

Commander must never hand-launch crew sessions. This wrapper launches crew work
FOREGROUND/BLOCKING by default, assigns a deterministic session name, records
durable launch metadata BEFORE the crew starts, captures stdout/stderr to
deterministic files, and verifies the expected result artifact exists before it
reports success. It refuses to launch a DUPLICATE crew for the same active
work-id/gate/role/worktree unless the prior attempt is explicitly abandoned, and
it supports explicit recovery (`--resume`/`--abandon --relaunch`) after a parent
session is lost.

Deliberate seams keep the wrapper fully testable without spawning a real agent:
  * `build_crew_argv(...)`  — PURE construction of the launcher command line.
  * `launch_process(...)`   — the ONLY place a real subprocess is spawned; tests
                              monkeypatch it to fake exit codes and to write (or
                              withhold) the result artifact.
  * registry read/write, session-name generation, duplicate detection, and
    result-artifact verification are PURE, directly-tested functions.

This wrapper does NOT advance gates, merge PRs, repair git, or integrate results;
that stays with Commander and the engine (#6 owns checklist leasing).

imports stdlib: __future__.annotations, argparse, dataclasses.dataclass, datetime.datetime, datetime.timezone, json, os, pathlib.Path, shutil, subprocess, sys
imported by: none found

```python
ACTIVE_STATUSES = {'running', 'resumable'}
DEFAULT_LAUNCHER = 'claude'
DISPATCH_SPAWN = 'spawn'
DISPATCH_EXTERNAL = 'external'
BACKEND_CLI = 'cli'
BACKEND_EXTERNAL = 'external'
BACKEND_AUTO = 'auto'
_CLI_DRIFT_MARKERS = ('unknown option', 'unrecognized arguments', 'unknown command')
```

- [CrewLaunchError](CrewLaunchError.md) class: A refusal: the requested launch/recovery is not allowed. No exit-0.
- [_now](_now.md) function: Current UTC time as an ISO-8601 string. Monkeypatch in tests to control
- [session_name](session_name.md) function: Deterministic, stable crew session name.
- [work_dir](work_dir.md) function: HOLE: no docstring
- [registry_path](registry_path.md) function: HOLE: no docstring
- [run_log_paths](run_log_paths.md) function: Deterministic stdout/stderr capture paths for one attempt.
- [load_registry](load_registry.md) function: Read the registry list; a missing file is an empty registry.
- [save_registry](save_registry.md) function: HOLE: no docstring
- [find_entry](find_entry.md) function: The entry whose session_name (== crew_id) matches `name`, or None.
- [is_abandoned](is_abandoned.md) function: HOLE: no docstring
- [active_duplicate](active_duplicate.md) function: The blocking duplicate, if any: an existing entry for the same
- [next_attempt](next_attempt.md) function: One past the highest attempt recorded for this gate/role/worktree (>=1).
- [result_exists](result_exists.md) function: Whether the expected result artifact exists. A relative path is resolved
- [result_fresh](result_fresh.md) function: Whether the expected result artifact exists AND is FRESH relative to the
- [build_crew_argv](build_crew_argv.md) function: PURE construction of the agent-CLI command line from role/handoff/model.
- [cli_drift_hint](cli_drift_hint.md) function: Actionable message when a failed launch looks like agent-CLI flag drift
- [_print_drift_hint_if_any](_print_drift_hint_if_any.md) function: Best-effort drift sniff on a failed launch's captured stderr.
- [launch_process](launch_process.md) function: The ONE place a real crew subprocess is spawned. Tests monkeypatch this to
- [crew_env](crew_env.md) function: UTF-8-safe environment defaults for the child (without clobbering an
- [process_alive](process_alive.md) function: Whether `pid` names a live process. The injectable PID-liveness seam used
- [_relativize](_relativize.md) function: Store paths in the registry relative to root when possible (matches the
- [_require_handoff](_require_handoff.md) function: Resolve the handoff path against root and REFUSE if it is missing. `action`
- [build_entry](build_entry.md) function: Construct the base `crew-runs.json` entry shared by BOTH backends (the
- [finalize_from_exit_code](finalize_from_exit_code.md) function: Finalize a spawned attempt's entry from the child exit code and result
- [entry_backend](entry_backend.md) function: The backend that owns a recorded entry. New entries carry `backend`
- [CrewSpec](CrewSpec.md) class: The parameters of one crew launch, passed to a backend's `dispatch`.
- [CrewBackend](CrewBackend.md) class: A pluggable crew-launch backend (Decision 1). Exactly two concrete
  - [CrewBackend.dispatch](CrewBackend.dispatch.md) method: Record the durable entry (running) BEFORE work. cli: spawn the
  - [CrewBackend.resume](CrewBackend.resume.md) method: cli: relaunch the subprocess with the stored session/handoff and
  - [CrewBackend.verify](CrewBackend.verify.md) method: Uniform across backends: exists-AND-fresh against the entry's
- [CliBackend](CliBackend.md) class: Spawn a headless `claude` CLI subprocess via the single `launch_process`
  - [CliBackend.dispatch](CliBackend.dispatch.md) method: HOLE: no docstring
  - [CliBackend.resume](CliBackend.resume.md) method: HOLE: no docstring
- [ExternalBackend](ExternalBackend.md) class: Record-only backend: the crew is dispatched out-of-band (an Agent-tool
  - [ExternalBackend.dispatch](ExternalBackend.dispatch.md) method: HOLE: no docstring
  - [ExternalBackend.resume](ExternalBackend.resume.md) method: HOLE: no docstring
- [select_backend](select_backend.md) function: Choose the crew-launch backend (Decision 4). PURE (given an injectable
- [launch_crew](launch_crew.md) function: Record the durable entry BEFORE launching, run the crew foreground, then
- [resume_crew](resume_crew.md) function: Continue a recorded crew using its STORED session name and handoff, routing
- [record_external_attempt](record_external_attempt.md) function: Record a durable crew-runs.json entry for an EXTERNALLY-dispatched crew
- [verify_external_result](verify_external_result.md) function: Verify whether the result artifact is present AND fresh for a recorded
- [abandon_crew](abandon_crew.md) function: Mark a prior attempt abandoned (releases its hold on the gate/worktree).
- [build_parser](build_parser.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
- [load_registry_for_resume](load_registry_for_resume.md) function: Resolve the registry that holds `session` by parsing the work-id from a

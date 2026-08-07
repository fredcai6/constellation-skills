# scripts.recover_crews
scripts/recover_crews.py, 243 lines, 3 holes

Recovery classifier over the durable crew-run registry.

After a parent-session loss it is ambiguous whether a crew is dead, running,
resumable, or already done. This reads `.agent-work/<work-id>/crew-runs.json`
and CLASSIFIES each recorded attempt from three facts only — its recorded
status, whether its PID is still alive, and whether its result artifact exists —
so Commander gets a durable, recoverable signal instead of guessing from
scattered process state.

Commander runs this before `execute` and before each crew dispatch, and may only
launch a new crew when recovery reports NO unresolved running/resumable/
conflicting attempt for the same work-id/gate/role/worktree.

`classify_entry` is a PURE function over (entry, alive_predicate,
result_exists_predicate); it never touches a real process or filesystem itself,
so every state is directly unit-tested. This module does NOT relaunch, advance
gates, repair git, or integrate results — it only reports.

imports stdlib: __future__.annotations, argparse, importlib.util, pathlib.Path, sys, typing.Callable
imported by: none found

```python
_RUN_CREW = Path(__file__).resolve().parent / 'run_crew.py'
_spec = importlib.util.spec_from_file_location('run_crew', _RUN_CREW)
run_crew = importlib.util.module_from_spec(_spec)
STATE_COMPLETE = 'complete'
STATE_ACTIVE = 'active'
STATE_RESUMABLE = 'resumable'
STATE_NEEDS_ABANDON = 'needs-abandon'
STATE_CONFLICT = 'conflict'
STATE_ABANDONED = 'abandoned'
STATE_FAILED = 'failed'
UNRESOLVED_STATES = {STATE_ACTIVE, STATE_RESUMABLE, STATE_CONFLICT}
AlivePredicate = Callable[[object], bool]
ResultPredicate = Callable[[dict], bool]
_BEHAVIOR = {STATE_COMPLETE: 'recoverable/complete; do not rerun', STATE_ACTIVE: 'active crew (pid ...
_EXTERNAL_RESUME_ACTION = "not running and no fresh result; an externally-dispatched crew is unrecoverable by the...
```

- [classify_entry](classify_entry.md) function: PURE recovery classification of one registry entry.
- [detect_conflicts](detect_conflicts.md) function: Pairs of entries that are BOTH active/resumable for the same
- [_behavior_for](_behavior_for.md) function: Human-readable behavior text for one classified entry. Uniform per state,
- [classify_registry](classify_registry.md) function: Classify every entry, upgrading members of a same-target collision to
- [_default_result_present](_default_result_present.md) function: HOLE: no docstring
  - [_default_result_present.predicate](_default_result_present.predicate.md) method: HOLE: no docstring
- [report](report.md) function: Print one human-readable line per entry plus a summary. Returns a nonzero
- [main](main.md) function: HOLE: no docstring

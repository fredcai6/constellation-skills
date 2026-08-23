# w3-door notes (commander)

## Understand — baseline reconciliation (2026-08-22)

Confirmed against actual code at commit 135c34eb (worktree HEAD, matches launch order's Base commit):

- `_crew_door_env` (scripts/run_crew.py:1323-1361): when `spine is None`, it returns
  `crew_env(parent=resolved_parent, scratch_dir=scratch_dir)` with no `spine_file`/
  `spine_session` args. `crew_env` (scripts/run_crew.py:1264-1320) defaults
  `base_env=None -> dict(os.environ)` and only assigns SPINE_FILE/SPINE_SESSION when the
  corresponding arg `is not None`; omitted means "leave whatever's already in `env` (i.e.
  the DISPATCHING process's own ambient os.environ) untouched." So a crew dispatched
  without `--spine` today inherits its dispatcher's SPINE_FILE + SPINE_SESSION verbatim.
  This is exactly the defect the launch order describes -- confirmed live, not assumed.
- Only two call sites of `_crew_door_env` in production code: `CliBackend.dispatch` (:1946)
  and `CliBackend.resume` (:2033). `crew_env` itself is called from nowhere else in the
  repo (grepped all *.py excluding tests and .agent-work archive snapshots) -- no other
  caller depends on `crew_env`'s generic "leave inherited when omitted" contract through a
  path this change touches.
- Honest-Null check: no caller found that legitimately depends on the inherited pair
  surviving through `_crew_door_env`. The clause does not trigger; proceeding with the fix.
- The test that currently CODIFIES the old (bad) behaviour and must flip:
  `tests/test_crew_launcher.py::DispatchDoorBindingTests::test_dispatch_without_spine_leaves_ambient_pair_untouched`
  (line ~1987) -- asserts a dispatched-without-`--spine` child's env carries the ambient
  SPINE_FILE/SPINE_SESSION verbatim. Must become an assertion that both are ABSENT.
- Docstrings needing edits (per launch order, non-optional): `_crew_door_env`'s own
  docstring (:1332-1339, "No `spine` means the inherited-environment route is genuinely
  untouched...") and `crew_env`'s docstring (:1276-1280, "...this is what lets the
  Admiral's own bootstrap...keep working"). `crew_env` itself is NOT being changed --
  only `_crew_door_env`'s handling of the `spine is None` branch. `crew_env`'s own
  generic "leave inherited when omitted" contract stays true and useful for other
  potential callers; its docstring's parenthetical needs to stop reading as blanket
  justification that inheriting is safe for a dispatched crew door, since that is
  precisely the case `_crew_door_env` no longer does that for.

## Mission (cited)

LAUNCH_ORDER:Mission -- clear SPINE_FILE and SPINE_SESSION together in `_crew_door_env`
when `spine is None`, instead of leaving them inherited. Edit both docstrings in the same
change. File scope: `scripts/run_crew.py` and its tests, exclusively.

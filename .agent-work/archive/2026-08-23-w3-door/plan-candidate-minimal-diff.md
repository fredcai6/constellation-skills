# Plan candidate — constraint: minimal-diff

Constraint: touch the smallest possible surface. Do not change `crew_env`'s signature or
behavior at all; express the clear entirely inside `_crew_door_env`.

## Gate plan

- **g1** (crew gate): implement + review
  - In `_crew_door_env`, when `spine is None`, build `env` via the existing
    `crew_env(parent=resolved_parent, scratch_dir=scratch_dir)` call, then explicitly
    `env.pop("SPINE_FILE", None)` and `env.pop("SPINE_SESSION", None)` before returning.
  - Update `_crew_door_env`'s docstring (run_crew.py:1332-1339) to state the new contract:
    no `spine` means the crew gets NO door — both vars are actively cleared, not inherited.
  - Update `crew_env`'s docstring (run_crew.py:1276-1280) to drop the "this is what lets
    ...keep working" framing that reads as blanket justification for inheriting being safe;
    clarify `crew_env`'s own generic "leave-untouched-when-omitted" contract is unaffected
    but `_crew_door_env` — the crew-dispatch door specifically — no longer relies on it for
    the `spine=None` branch.
  - Flip `tests/test_crew_launcher.py::DispatchDoorBindingTests::test_dispatch_without_spine_leaves_ambient_pair_untouched`
    to assert both vars are ABSENT from the dispatched child's env, and rename it to
    `test_dispatch_without_spine_gets_no_door` (name no longer matches new behavior).
    Update its docstring/comment accordingly.
  - Add one new test exercising `resume` (not just `dispatch`) without a stored spine,
    confirming the same clearing applies via `_crew_door_env`'s single implementation
    (both call sites share the helper, so one shared assertion suffices, but resume's own
    ambient-inheritance path is currently untested and is the other call site named in the
    mission).
  - Run `python3 -m pytest -q tests/test_crew_launcher.py` and the full suite before
    closing the gate.

## Tradeoffs

- + Smallest possible diff; zero risk to `crew_env`'s other (hypothetical/future) callers.
- + `crew_env` keeps one simple, well-tested contract: assign when given, else leave
  untouched. All the "does this door get cleared" logic lives in exactly one place
  (`_crew_door_env`), matching the mission's own framing ("in `_crew_door_env`, make...").
- - `crew_env` is left with a residual "leave inherited" behavior that is exactly the
  hazard being fixed one layer up — a future caller of `crew_env` directly (bypassing
  `_crew_door_env`) could reintroduce the same leak. Mitigated: grepped, no such caller
  exists today; `crew_env` is only ever called from `_crew_door_env`.

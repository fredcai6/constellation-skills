# Implementation Result

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3-implement`

## Completed slice
Wired g2's `resolve_model` into `CrewSpec.__post_init__` (the class the handoff
calls `CrewLaunchSpec` is actually named `CrewSpec` in `scripts/run_crew.py` —
confirmed by grep before editing; there is no separate `CrewLaunchSpec`).
`--reason` is threaded CLI flag -> `CrewSpec` field -> `build_entry` at both
call sites -> `main()`'s fresh-launch **and** `--abandon --relaunch`
constructions (attempt 2: the two call sites are now symmetric, per Ruling 2
below). All four `CrewSpec(...)` construction sites resolve through the
choke point automatically.

This is **attempt 2**, rework per two rulings from the Admiral on attempt 1's
stop (`.agent-work/567-j/crew-handoffs/g3-implement-rework-handoff.md`), both
within the Admiral's own file ownership (`scripts/run_crew.py`, its tests):

- **Ruling 1** — the three additional failing tests attempt 1 surfaced and
  correctly stopped on: fix all three, in scope. Done (below).
- **Ruling 2** — the `--abandon --relaunch` reason asymmetry attempt 1 flagged
  under Assumptions: fix it, in scope, plus one new test. Done (below).

## Scope
**Files changed:**
- `scripts/run_crew.py` — everything attempt 1 already had (`CrewSpec.reason`
  field, `CrewSpec.__post_init__`, `build_entry` (`reason` param + write),
  both `build_entry(...)` call sites, `build_parser` (`--reason`), `main()`'s
  fresh-launch `CrewSpec(...)` construction, docstring updates), **plus this
  attempt**: `reason=args.reason` added to `main()`'s `--abandon --relaunch`
  `CrewSpec(...)` construction (Ruling 2), making it exactly parallel to the
  fresh-launch site.
- `tests/test_crew_launcher.py` — everything attempt 1 already had, **plus
  this attempt**:
  - `MandatoryModelTests::test_crew_spec_refuses_falsy_model_directly`
    rewritten (now `test_crew_spec_with_falsy_model_resolves_the_role_default`)
    to assert `CrewSpec(role="reviewer", model=None)` resolves to `"sonnet"`
    instead of raising. The "undeclared pair still refuses" case was already
    covered by the existing `test_unpopulated_harness_is_refused_by_name_even_with_model_given`
    (role="implementer", launcher="codex") — confirmed, not duplicated.
  - `ExternalDispatchTests::test_cli_parser_persists_model_and_reasoning_effort_to_external_registry`
    rewritten: `--model gpt-5.6` swapped for `--model haiku` (implementer's
    real, in-table, non-default tier) with `--reason "budget-constrained
    dispatch, haiku sufficient for this handoff"`; now asserts the registry
    entry's `model`, `reason`, and `reasoning_effort` fields all persist.
  - `BackendEquivalenceTests::test_external_dispatch_records_without_spawning_returns_none`
    rewritten: `CrewSpec(role="implementer", model="opus")` swapped for
    `model="sonnet"` (implementer's default, needs no `--reason`) — smallest
    change preserving the test's actual intent (no spawn, returns `None`).
  - New `MandatoryModelTests::test_abandon_relaunch_with_reason_succeeds_and_entry_carries_reason`,
    mirroring `test_non_default_in_set_model_with_reason_succeeds_and_entry_carries_reason`:
    `--abandon --relaunch --model haiku --reason "cheap smoke-test lane"`
    succeeds and the relaunched entry carries both `model` and `reason`.

**Specific exclusions touched:** no. `resume_crew()`, `CliBackend.resume()`,
and `ExternalBackend.resume()` show **zero** diff — confirmed again this
attempt by inspecting every `git diff scripts/run_crew.py` hunk header (12
hunks; none falls inside `resume_crew` at line 2010+, `CliBackend.resume` at
1687-1764, or `ExternalBackend.resume` at 1835-2010). `launch_crew()`/
`record_external_attempt()` signatures remain unchanged (not in Allowed
Scope) — their `CrewSpec(...)` constructions get resolution "for free" via
`__post_init__`.

## Behavior changed
Yes, same as attempt 1, **plus**: an `--abandon --relaunch` dispatch with a
non-default in-set `--model` and a `--reason` now succeeds and records the
reason on the relaunched entry — previously (attempt 1) only the fresh-launch
path accepted `--reason`; the relaunch path silently dropped it, so a
relaunch could re-resolve to the default or repeat the same default
explicitly, but never override with a reasoned non-default choice. The two
call sites are now symmetric.

## Test mode
**Required:** `test-after for the wiring; TDD for the five new/rewritten behavioral tests`
**Satisfied:** yes. All rewrites/new tests this attempt assert the intended
resolved-default / refuse-by-name / reason-persists shapes directly, written
and run against the wiring already in place from attempt 1 (mechanical,
trusted per the handoff's "test-after allowed for the wiring" clause).

## Evidence

### Wiring grep (exactly one call site required)
```bash
$ grep -rn "resolve_model" --include=*.py scripts/run_crew.py | grep -v "def resolve_model"
842:# (decision:harness-dimension-is-required). `resolve_model` below refuses,
863:    """The tier `resolve_model` picked, and the `--reason` (if any) that
1446:    `resolve_model`: a role/harness pair WITH a `ROLE_MODEL_TIERS` entry now
1483:        resolved = resolve_model(
```
Only line 1483 is an actual call (the other three are prose/docstring
references to the name). **Count of real call sites: 1**, inside
`CrewSpec.__post_init__`, as required. Unchanged from attempt 1.

### Every `CrewSpec(` construction site
```bash
$ grep -n -B2 "spec = CrewSpec(" scripts/run_crew.py
2002:    spec = CrewSpec(     # inside launch_crew() — public wrapper
2068:    spec = CrewSpec(     # inside record_external_attempt() — public wrapper
2363:            spec = CrewSpec(   # inside main(), --abandon --relaunch path — now passes reason=args.reason
2387:        spec = CrewSpec(       # inside main(), fresh-launch path
```
All four go through `CrewSpec.__post_init__` — and therefore through
`resolve_model` — by Python's own construction semantics. The two `main()`
sites (2363, 2387) are now symmetric: both pass `reason=args.reason`.

### `resume_crew()` zero-diff confirmation
```bash
$ git diff scripts/run_crew.py | grep -n "^@@"
5:@@ -834,6 +834,86 @@ def build_crew_argv(
92:@@ -1120,6 +1200,7 @@ def build_entry(
100:@@ -1142,6 +1223,11 @@ def build_entry(
112:@@ -1211,6 +1297,8 @@ def build_entry(
121:@@ -1352,7 +1440,17 @@ class CrewSpec:
140:@@ -1365,6 +1463,7 @@ class CrewSpec:
148:@@ -1381,12 +1480,11 @@ class CrewSpec:
166:@@ -1554,7 +1652,7 @@ class CliBackend(CrewBackend):
175:@@ -1709,7 +1807,7 @@ class ExternalBackend(CrewBackend):
184:@@ -2030,6 +2128,7 @@ def build_parser() -> argparse.ArgumentParser:
192:@@ -2266,7 +2365,7 @@ def main(argv: list[str] | None = None) -> int:   # abandon-relaunch: reason=args.reason added
201:@@ -2289,7 +2388,7 @@ def main(argv: list[str] | None = None) -> int:   # fresh-launch: unchanged from attempt 1
```
12 hunks. None falls inside `resume_crew()` (line 2010+ post-edit),
`CliBackend.resume()` (1687-1764), or `ExternalBackend.resume()`
(1835-2010). `resume_crew()` has **zero** changes, exactly as required.

### Old-shape registry entry round-trip
Unchanged from attempt 1: `test_old_shape_registry_entry_with_model_and_no_reason_key_resumes_cleanly`
still passes, still safe by construction (`CliBackend.resume()` never
constructs a `CrewSpec` and never looks up `"reason"`).

### Full test run
```bash
$ py -m pytest tests/test_crew_launcher.py -q
........................................................................ [ 30%]
........................................................................ [ 60%]
........................................................................ [ 91%]
....................F                                                    [100%]
=================================== FAILURES ===================================
_ ScratchDirResumeTests.test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound _
...
E           AssertionError: 'CREW_SCRATCH_DIR' unexpectedly found in {...}
tests/test_crew_launcher.py:4326: AssertionError
=========================== short test summary info ============================
FAILED tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound
1 failed, 236 passed in 0.87s
```
**Final tally: 236 passed, 1 known-unrelated failed.** The one remaining
failure is the pre-existing/environmental `CREW_SCRATCH_DIR` leak
(`ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`)
— confirmed pre-existing by attempt 1 via `git stash` isolation (fails
identically on the pre-g2/pre-g3 baseline; the test doesn't isolate the
crew's own ambient `CREW_SCRATCH_DIR` from `os.environ`). Named in the
rework handoff's own text as the one failure that may remain, out of scope
for this gate. All three tests named in Ruling 1, plus the two originally
rewritten `MandatoryModelTests` cases, plus the new Ruling 2 test, are
green.

## Docs/contracts touched
- none

## Assumptions
- Same as attempt 1: `CrewLaunchSpec` in the handoff refers to `CrewSpec`
  (only matching class in the file, not frozen — plain attribute assignment
  in `__post_init__`, not `object.__setattr__`).
- The abandon-relaunch asymmetry flagged under Assumptions in attempt 1 is
  now resolved per Ruling 2 — no longer an open assumption.

## Stop conditions hit
None this attempt. Both rulings from the rework handoff were unambiguous and
within the Admiral's stated file ownership; no new issue surfaced.

## Out-of-scope observations
- none.

## Workflow Feedback
- **What worked:** The rework handoff's rulings were concrete enough to apply
  directly — each named the exact test, the exact swap-in value, and the
  reasoning behind preserving each test's original intent, so no further
  float was needed.
- **Handoff gaps (carried from attempt 1, now moot but worth keeping for the
  next gate that wires a shared choke point like this):** a pre-flight grep
  of existing test fixtures against a new validation table's populated
  keys (e.g. `grep -n 'model="' tests/test_crew_launcher.py` against
  `ROLE_MODEL_TIERS`'s populated roles/harnesses) would have surfaced all
  three collisions before attempt 1's implementation pass instead of at the
  pytest-run stage.

## Return status
`complete`

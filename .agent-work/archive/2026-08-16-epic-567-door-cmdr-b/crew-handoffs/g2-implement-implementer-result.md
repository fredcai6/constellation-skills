# Implementation Result

## Assigned gate
`g2-implement`

## Completed slice
Fixed the 3 net-regression tests the Admiral diagnosed as passing only because of the
mtime-only contract g1 deleted (#432). Both call sites now pass
`accept_mtime_only_risk=<honest reason>` to `RC.verify_external_result(...)`, naming what
each test actually proves (registry addressing; identity-free delivery discovery) rather
than a fictitious spine. No production code touched.

## Scope
**Files changed:**
- `tests/test_work_id_nesting.py` (1 call site, inside `_verify_round_trip`, shared by both
  fixed tests)
- `tests/test_crew_delivery_addressing.py` (1 call site, inside the `for asking_instance in
  (...)` loop)

**Specific exclusions touched:** no — `scripts/run_crew.py`,
`scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `tests/test_crew_launcher.py`,
`tests/test_episode_observations.py`, `tests/test_code_map.py` were not edited.

## Behavior changed
Yes, test-only: two `assertTrue(fresh, ...)` sites that previously exercised the deleted
mtime-only default now explicitly opt into the loud, recorded `accept_mtime_only_risk`
escape hatch shipped with g1's default-refuse fix, with a reason honestly naming what each
scenario proves (neither has any spine concept in scope). `ExternalBackend.verify()`'s
refusal itself is untouched and unweakened.

## Map Impact
- **Structural anchors touched:** `scripts/run_crew.py:verify_external_result` — read-only,
  confirmed unchanged; its `accept_mtime_only_risk` kwarg (added in g1, PR #621) is now
  exercised by two more callers.
- **Capabilities added/changed/affected:** none — no new capability; two existing test
  scenarios now use the existing escape hatch instead of the deleted mtime-only default.
- **Constraints/assumptions touched:** `decision:and-not-rescue-semantics` and
  `decision:default-refuse-not-default-warn` (both g1 MISSION_FRAME.md, same work area) —
  these two fixes confirm the escape hatch is reachable and honestly labeled for
  non-spine-driving scenarios; they do not relitigate or weaken the refusal.
- **Claims/evidence produced:** `tests/test_work_id_nesting.py::CrewRegistryAddressingTests`
  (both tests) and
  `tests/test_crew_delivery_addressing.py::JobAddressedDeliverySurvivesRelaunch::test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity`
  now assert the NEW default-refuse contract via the escape hatch, replacing the stale
  mtime-only-default assertion.
- **Trust limitations / drift found:** none found in this gate's scope.

## Test mode
**Required:** `Fix-forward (pre-existing tests whose assertions predate g1's fix; RED
observed against current tree before edit, GREEN after)`
**Satisfied:** yes — each of the 3 named tests was run RED before its edit and GREEN after,
verbatim below.

## Evidence

### 1. `tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_flat_work_id_finalizes_identically` and `::test_nested_work_id_finalizes_its_own_registry`

RED (before edit):
```
cd /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend && python -m pytest tests/test_work_id_nesting.py -k "test_flat_work_id_finalizes_identically or test_nested_work_id_finalizes_its_own_registry" -q
```
```
FF                                                                       [100%]
=================================== FAILURES ===================================
_____ CrewRegistryAddressingTests.test_flat_work_id_finalizes_identically ______
...
>       self.assertEqual("completed", self._verify_round_trip(FLAT)["status"])
tests/test_work_id_nesting.py:123: in test_flat_work_id_finalizes_identically
tests/test_work_id_nesting.py:109: in _verify_round_trip
    self.assertTrue(fresh, "the result artifact was written, so it must read fresh")
E   AssertionError: False is not true : the result artifact was written, so it must read fresh
__ CrewRegistryAddressingTests.test_nested_work_id_finalizes_its_own_registry __
...
>       self.assertEqual("completed", self._verify_round_trip(NESTED)["status"])
tests/test_work_id_nesting.py:117: in test_nested_work_id_finalizes_its_own_registry
tests/test_work_id_nesting.py:109: in _verify_round_trip
    self.assertTrue(fresh, "the result artifact was written, so it must read fresh")
E   AssertionError: False is not true : the result artifact was written, so it must read fresh
=========================== short test summary info ============================
FAILED tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_flat_work_id_finalizes_identically
FAILED tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_nested_work_id_finalizes_its_own_registry
2 failed, 26 deselected in 0.04s
```

Edit: `_verify_round_trip`'s single `RC.verify_external_result(...)` call now passes
`accept_mtime_only_risk="test: exercising registry addressing (nested vs flat work_id), not spine-driving"`.

GREEN (after edit):
```
cd /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend && python -m pytest tests/test_work_id_nesting.py -k "test_flat_work_id_finalizes_identically or test_nested_work_id_finalizes_its_own_registry" -q
```
```
..                                                                       [100%]
2 passed, 26 deselected in 0.03s
```

### 2. `tests/test_crew_delivery_addressing.py::JobAddressedDeliverySurvivesRelaunch::test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity`

RED (before edit):
```
cd /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend && python -m pytest tests/test_crew_delivery_addressing.py -k test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity -q
```
```
F                                                                        [100%]
=================================== FAILURES ===================================
_ JobAddressedDeliverySurvivesRelaunch.test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity _
...
                fresh, verified_entry = RC.verify_external_result(
                    reloaded_entries, session, root,
                )
>               self.assertTrue(
                    fresh, f"{asking_instance}: run_crew.verify_external_result "
                    f"did not find the result fresh",
                )
E               AssertionError: False is not true : commander-w4-467-i: run_crew.verify_external_result did not find the result fresh

tests/test_crew_delivery_addressing.py:181: AssertionError
=========================== short test summary info ============================
FAILED tests/test_crew_delivery_addressing.py::JobAddressedDeliverySurvivesRelaunch::test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity
1 failed, 3 deselected in 0.03s
```

Edit: the single `RC.verify_external_result(...)` call inside the `for asking_instance in
(...)` loop now passes
`accept_mtime_only_risk=f"test: {asking_instance} proving identity-free delivery discovery (job-file-not-agent-file), not spine-driving"`.

GREEN (after edit):
```
cd /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend && python -m pytest tests/test_crew_delivery_addressing.py -k test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity -q
```
```
.                                                                        [100%]
1 passed, 3 deselected in 0.02s
```

### Full file runs (after edits, both files together)
```
cd /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend && python -m pytest tests/test_work_id_nesting.py tests/test_crew_delivery_addressing.py -q
```
```
................................                       [100%]
32 passed, 18 subtests passed in 0.60s
```
No other test in either file changed behavior — the 3 named tests are the only ones whose
outcome flipped; the rest were already green and unmodified.

### g1's own suite (regression check — no production code touched)
```
cd /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend && python -m pytest tests/test_crew_launcher.py -q
```
```
217 passed in 0.72s
```

**Result:** pass — all three named tests fixed, full-file runs green, g1's suite unaffected.

## TDD evidence, if required
- Failing test observed: pasted verbatim above (RED sections), for both call sites.
- Passing test observed: pasted verbatim above (GREEN sections), for both call sites.
- Refactor while green: no — one-line-per-call keyword additions only, nothing to refactor.

## Docs/contracts touched
- none

## Assumptions
- none — the fix (flag, reason-wording style) was fully specified by the Admiral's
  diagnosis relayed in the handoff; no judgment calls were needed beyond wording the two
  reason strings to name what each test actually proves, as instructed.

## Stop conditions hit
- none — neither fix required touching `scripts/run_crew.py` or any file outside Allowed
  Scope; both failures were exactly the mtime-only `assertTrue(fresh, ...)` assertion
  described in the handoff.

## Out-of-scope observations
- none

## Workflow Feedback

- **Handoff gaps:** none — the handoff named the exact files, line numbers, exact keyword,
  and exact reason-string style; both edits matched the handoff's described call sites and
  exact context byte-for-byte on first read, no ambiguity encountered.
- **Context rediscovered:** the `constellation-implementer` skill's referenced
  `references/checklist-engine.md` doesn't exist at that path under the skill directory
  (only in `constellation-workbench`'s `references/`); I resolved it by reading
  `constellation-workbench`'s copy directly, and confirmed via the "dogfooding" note there
  that the CLI script is `scripts/checklist_engine.py` at the repo root (vendored) rather
  than under any skill's `scripts/` dir on this dogfooding repo. Also: the engine's `attest`
  verb takes `--note`, not `--why` (that flag belongs to `advance`) — the plan template's
  own inline guidance doesn't call this asymmetry out, so the first `attest` call in this
  run failed on `unrecognized arguments: --why` before I found the correct flag via `attest
  -h`.
- **Instructions improvised around:** none beyond the `--note`/`--why` flag-name mismatch
  above, which I resolved by reading `--help` rather than guessing further.
- **What would have made this easier:** cross-link
  `constellation-implementer/references/checklist-engine.md` to the actual file location
  (`constellation-workbench/references/checklist-engine.md`) so a first-time reader doesn't
  need to search the filesystem for it; and note in the engine reference doc that `attest`
  uses `--note` while `advance` uses `--why`, since both are "explain your reasoning to the
  engine" calls and the naming difference is easy to trip on.

## Return status
`complete`

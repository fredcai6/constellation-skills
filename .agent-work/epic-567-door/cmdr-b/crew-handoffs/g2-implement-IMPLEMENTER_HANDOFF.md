# Implementer Handoff

## Gate
g2

## Task
The Admiral diagnosed 3 net-regression tests in the full suite that were passing ONLY
because of the mtime-only clean-pass g1 deleted (#432). Fix these 3 tests so they assert
the NEW contract instead of the deleted one, without weakening `ExternalBackend.verify()`'s
refusal in any way to make them pass.

All three currently fail on `self.assertTrue(fresh, "the result artifact was written, so
it must read fresh")` (or an equivalent inline assertion) — this is the mtime-only
contract stated as a test assertion. Each of these three tests is actually testing
something UNRELATED to spine-driving (registry addressing for nested vs. flat work ids;
identity-free crew-delivery discovery on a relaunch) — none of them has any spine concept
in scope at all. The correct fix, per the Admiral's explicit instruction, is the
`--accept-mtime-only-risk` escape hatch (not naming a fictitious spine), since these
scenarios genuinely have nothing to check a spine against.

### 1. `tests/test_work_id_nesting.py::CrewRegistryAddressingTests`

`_verify_round_trip(self, work_id)` (around line 88) calls:
```python
fresh, verified = RC.verify_external_result(entries, entry["session_name"], root)
self.assertTrue(fresh, "the result artifact was written, so it must read fresh")
```
Change the call to pass the new keyword:
```python
fresh, verified = RC.verify_external_result(
    entries, entry["session_name"], root,
    accept_mtime_only_risk="test: exercising registry addressing (nested vs flat work_id), not spine-driving",
)
```
This single helper is shared by both failing tests
(`test_flat_work_id_finalizes_identically`, `test_nested_work_id_finalizes_its_own_registry`)
— one change fixes both. Do not touch any other test in this file (the rest already pass
and are about session-name parsing, not verification).

### 2. `tests/test_crew_delivery_addressing.py::JobAddressedDeliverySurvivesRelaunch::test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity`

Around line 178, inside the `for asking_instance in (...)` loop:
```python
fresh, verified_entry = RC.verify_external_result(
    reloaded_entries, session, root,
)
self.assertTrue(
    fresh, f"{asking_instance}: run_crew.verify_external_result "
    f"did not find the result fresh",
)
```
Add the same keyword, with a reason naming what THIS test actually proves:
```python
fresh, verified_entry = RC.verify_external_result(
    reloaded_entries, session, root,
    accept_mtime_only_risk=f"test: {asking_instance} proving identity-free delivery discovery (job-file-not-agent-file), not spine-driving",
)
```
This call is inside a loop over two `asking_instance` values — the kwarg must be present
on both loop iterations' call (it already will be, since it is one line inside the loop
body — just confirm you have not accidentally duplicated the call outside the loop).

## Protected Intent
The new default-refuse contract on `ExternalBackend.verify()` (built in g1, this same
lane, PR #621) must not be weakened, worked around, or bypassed by these test changes —
each fix uses the SAME explicit, loud, recorded escape hatch the fix itself ships
(`--accept-mtime-only-risk`), naming honestly why THIS scenario has no spine to check,
never a blanket "accept everything" change to production code.

## Test Mode
Fix-forward, not TDD in the usual sense — these are pre-existing tests whose assertions
predate g1's fix and now correctly fail against it. Run each test red (against the current
tree, before your edit) to confirm you understand exactly why it fails, then green after
your one-line-per-call edit.

## Close Criteria
- `tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_flat_work_id_finalizes_identically` passes.
- `tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_nested_work_id_finalizes_its_own_registry` passes.
- `tests/test_crew_delivery_addressing.py::JobAddressedDeliverySurvivesRelaunch::test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity` passes.
- No other test in either file changes behavior (both files' full suite still green,
  same pass count as before your edit minus these 3).
- No production code in `scripts/run_crew.py` is touched — this gate is test-file-only.
- `tests/test_crew_launcher.py` (g1's own suite) still shows 217 passed, unaffected.

## Allowed Scope
- `tests/test_work_id_nesting.py`
- `tests/test_crew_delivery_addressing.py`

## Specific Exclusions
- `scripts/run_crew.py` — no production code change. If a fix seems to need one, STOP —
  that would mean the diagnosis is wrong, and this gate does not have authority to
  re-litigate g1's design.
- `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py` — fenced, lane A this wave.
- `tests/test_crew_launcher.py`, `tests/test_episode_observations.py`,
  `tests/test_code_map.py` — out of this gate's scope (handled separately by the
  Commander directly, not this crew).

## Constraints
- Match the exact `accept_mtime_only_risk=` keyword name (already implemented in
  `scripts/run_crew.py`'s `verify_external_result`, g1's own fix — read its signature
  before editing if anything here is unclear).
- Each reason string should say, briefly, what the test actually proves instead — not a
  generic "no spine given."

## Map Anchors (inbound)
- **Structural:** `scripts/run_crew.py:verify_external_result` (read-only — the function
  signature you are calling into; already accepts `accept_mtime_only_risk` as an optional
  kwarg per g1's fix), `tests/test_work_id_nesting.py:CrewRegistryAddressingTests._verify_round_trip`,
  `tests/test_crew_delivery_addressing.py:JobAddressedDeliverySurvivesRelaunch`.
- **Decision anchors:** `decision:and-not-rescue-semantics`,
  `decision:default-refuse-not-default-warn` (both from g1's MISSION_FRAME.md, this same
  work area) — these tests confirm the escape hatch is reachable and honestly labeled,
  they do not relitigate the refusal itself.
  `@grade: settled/measured · leans g2-implement`

## Deliverable Path Check
- **Committed** — `tests/test_work_id_nesting.py`; `git check-ignore` exits 1.
- **Committed** — `tests/test_crew_delivery_addressing.py`; `git check-ignore` exits 1.

## Required Evidence
- Each of the 3 named tests: RED (before your edit) and GREEN (after), pasted verbatim.
- Full file runs: `pytest tests/test_work_id_nesting.py tests/test_crew_delivery_addressing.py -q` before and after.
- `pytest tests/test_crew_launcher.py -q` after your edit — confirm still 217 passed (g1's suite unaffected).

## Wiring Grep
```bash
grep -n "accept_mtime_only_risk" tests/test_work_id_nesting.py tests/test_crew_delivery_addressing.py
```
State the count found (expect exactly 1 in each file, at the two call sites named above).

## Verification Commands
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend && python -m pytest tests/test_work_id_nesting.py tests/test_crew_delivery_addressing.py tests/test_crew_launcher.py -q
```

## Suggested Model Tier
simple bounded — two one-line-per-call test edits, exact fix already specified.

## Authority
The fix (which flag, which reason wording style) is already decided by the Admiral's
diagnosis message, relayed verbatim above. Do not choose a different mechanism (e.g. do
not name a fictitious `--spine` path for these scenarios — they have none).

## Stop Conditions
Stop and return if: the fix would require touching `scripts/run_crew.py` or any file
outside Allowed Scope; either test's failure reason turns out to be something other than
the mtime-only assertion described above.

## Return Format
Return IMPLEMENTER_RESULT to
`.agent-work/epic-567-door/cmdr-b/crew-handoffs/g2-implement-implementer-result.md` before
ending your turn.

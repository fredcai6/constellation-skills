# Reviewer Handoff

## Gate
g1

## Survey State Location
`.agent-work/w3-door/g1-review/review.json`

## What Was Implemented
`_crew_door_env` (in `scripts/run_crew.py`) now actively clears `SPINE_FILE` and
`SPINE_SESSION` from the returned env when `spine is None`, instead of leaving whatever
the dispatching process's own ambient environment happens to carry. A crew dispatched (or
resumed) with no `--spine` now gets NO door at all. Both affected docstrings (`crew_env`'s
and `_crew_door_env`'s) were updated. The test suite in `tests/test_crew_launcher.py` was
extended/rewritten: one rename+rewrite, one new resume test, two heartbeat tests rewritten.
Already committed at `e11801972c63c969be88f904afe0fa9bbb6d8fad` on branch `epic-569/w3-door`.

## How to Inspect the Diff
`git show e11801972c63c969be88f904afe0fa9bbb6d8fad` (or `git diff 135c34eb..e1180197 --
scripts/run_crew.py tests/test_crew_launcher.py`) — the change is committed, working tree
is clean against it. Base commit is `135c34eb` (origin/main at dispatch time).

## Task Statement
In `scripts/run_crew.py`, make `_crew_door_env` explicitly CLEAR `SPINE_FILE` and
`SPINE_SESSION` when `spine` is `None`, instead of leaving the dispatching process's
ambient pair inherited — so a crew dispatched without `--spine` gets NO door, never a
door onto a spine it does not own. Both docstrings that asserted inheritance was the safe,
documented behavior must be corrected in the same change. `decision:clear-both-or-neither`
is fixed: clear both vars together, never one alone.

## Close Criteria
- `_crew_door_env`, when `spine is None`, returns an env with neither `SPINE_FILE` nor
  `SPINE_SESSION` present, even when the dispatching process's own ambient environment
  carries both.
- `_crew_door_env`'s docstring no longer asserts "...exactly as `crew_env()`'s own contract
  already promises" (or any equivalent claim that inheriting is safe) — states the new
  contract instead: no `spine` means NO door.
- `crew_env`'s docstring drops the "(this is what lets the Admiral's own bootstrap...)"
  framing and states `crew_env`'s own contract is unchanged, but `_crew_door_env` no
  longer relies on it for the `spine=None` branch.
- `crew_env` itself is unchanged (signature, body, direct-caller contract).
- `tests/test_crew_launcher.py::DispatchDoorBindingTests::test_dispatch_without_spine_leaves_ambient_pair_untouched`
  is renamed and rewritten to assert `SPINE_FILE`/`SPINE_SESSION` are ABSENT (not equal to
  ambient values).
- The dangling cross-reference in `test_dispatch_without_spine_binds_neither_var`'s comment
  is updated to name the renamed test.
- A new test covers `CliBackend().resume(...)` with no stored spine, using REAL non-empty
  ambient values (not `no_ambient_spine_env()`-stripped, which would prove nothing about
  active clearing).
- `ParentLeaseHeartbeatTests::test_dispatch_skips_parent_heartbeat_in_shared_spine_case`
  and `test_resume_skips_parent_heartbeat_in_shared_spine_case` are rewritten (not left
  asserting an impossible scenario) to assert the NEW correct behavior: a `spine=None`
  dispatch/resume from a door-bound parent now ALWAYS starts the parent heartbeat, since
  the child gets no door and cannot maintain the parent's lease itself.
- `_parent_lease_heartbeat`'s own comparison logic is untouched.
- Full suite green (`python3 -m pytest -q`) except the ONE known pre-existing, unrelated
  failure: `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
  fails because this gate's one new test method bumps `map/INDEX.md`'s committed entity
  count by one (5723 -> 5724); confirm via `git stash`/`git stash apply` against the base
  commit that this SAME test passes there (i.e. this failure is caused by this diff, but
  is a map-freshness bookkeeping artifact, not a behavioral regression, and regenerating
  `map/INDEX.md` is out of this lane's file ownership this wave — three sibling lanes are
  editing other files concurrently). Any OTHER failure is a BLOCK.

## Allowed Scope
`scripts/run_crew.py` and `tests/test_crew_launcher.py` only.

## Specific Exclusions
No change to `crew_env`'s signature/behavior, `--spine`'s meaning, `SPINE_PARENT`,
`CREW_SCRATCH_DIR`, the registry schema, or `_parent_lease_heartbeat`'s comparison logic.
No file outside the two named above (verify `git show --stat` on the commit lists exactly
these two).

## Constraints the Implementation Must Respect
- `decision:clear-both-or-neither` — both vars cleared together, never one alone.
  `@grade: settled/admiral · leans g1-implement,g1-review`
- `decision:verify-against-a-real-child` — acceptance evidence is a real dispatched
  child, not only a unit-test env-dict assertion.
  `@grade: settled/human · leans g1-review,g1-integrate`

## Map Anchors (inbound)
Map is DEGRADED-UNPARSEABLE (`.agent-work/w3-door/map-orientation.json`) — no citable
anchor exists for this symbol.
- **Structural:** `scripts/run_crew.py:1264` `crew_env`, `scripts/run_crew.py:1323`
  `_crew_door_env`, `scripts/run_crew.py:1763` `_parent_lease_heartbeat` (read-only
  reference, unchanged).
- **Decision anchors:** decision:clear-both-or-neither
  `@grade: settled/admiral · leans g1-implement,g1-review`; decision:verify-against-a-real-child
  `@grade: settled/human · leans g1-review,g1-integrate`
- **Evidence expectations:** `python3 -m pytest -q` (full suite) green modulo the one
  named pre-existing map-freshness failure.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/w3-door/crew-handoffs/g1-implement-result.md` (status
`complete`): full docstring diff, `tests/test_crew_launcher.py` green (262/262), full
suite (3729 passed, 9 skipped, 1 failed — the named map-freshness artifact), a direct
`_crew_door_env` call confirming clearing behavior. The Commander independently
reproduced all of this against the actual committed diff before dispatching you (git diff
matched the claim exactly, tests reproduced, full suite reproduced with the same single
pre-existing failure confirmed via git stash/apply against the base commit) and ran a
genuine real-dispatched-child spot-check (`run_crew.py --backend cli` spawning a real OS
subprocess with a fake `claude` launcher binary that dumps its own actual process
environment) confirming SPINE_FILE/SPINE_SESSION are absent from the real child's env even
with a real ambient pair set in the dispatcher.

## Suggested Model Tier
simple bounded — narrow, fully-specified diff on one commit; sonnet per launch order
Budget.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or
unverifiable, a policy decision is required before a verdict is possible, or you find any
suite failure outside the one named pre-existing map-freshness artifact.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers,
out-of-scope observations, workflow feedback. Write the full REVIEW_RESULT to
`.agent-work/w3-door/crew-handoffs/g1-reviewer-result.md` before ending your turn.

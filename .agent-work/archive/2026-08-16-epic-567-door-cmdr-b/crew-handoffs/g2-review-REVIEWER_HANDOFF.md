# Reviewer Handoff

## Gate
g2

## Survey State Location
`.agent-work/epic-567-door/cmdr-b/g2-review/review.json`.

## What Was Implemented
Post-return rework, requested directly by the Admiral (this epic's authority above the
frozen launch order) after diagnosing 6 net regressions in PR #621 (g1's #432 fix) against
`main`. This gate covers groups 1 and 2 of that diagnosis only (group 3, a stale generated
`map/INDEX.md`, was explicitly withdrawn by the Admiral in a follow-up correction — leave
`tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
red; do NOT regenerate `map/INDEX.md`, and flag it as a BLOCK if you find it touched).

**Group 1** — 3 tests that were passing only because of the mtime-only clean-pass g1
deleted, now failing on `assertTrue(fresh, ...)`. Both call sites (one shared by 2 tests in
`tests/test_work_id_nesting.py`, one in `tests/test_crew_delivery_addressing.py`) now pass
`accept_mtime_only_risk="<honest reason>"` to `RC.verify_external_result(...)`, naming what
each test actually proves (registry addressing; identity-free delivery discovery) — neither
scenario has any spine concept in scope, so the escape hatch (not a fictitious `--spine`) is
the correct fix per the Admiral's own instruction. No production code touched.

**Group 2** — episode `epic-567-door_cmdr-b-003` assertion `a5` tripped the strict
imperative-detector guard on a past-tense/imperative homograph ("read"). Fixed via
`restate-assertion` (the only write path into `episodes/`), rephrasing "read" → "reading"
to remove the ambiguity while preserving the original meaning — NOT by adding to the
guard's exception list (the Admiral explicitly forbade that, since the list is already 11
entries long from 4 prior runs absorbing the same pattern). A new triage candidate
(`tc3-imperative-detector-homograph-allowlist-growth.md`) records this as a "check whose
failures are absorbed rather than diagnosed" observation — not filed, per this lane's
`decision:no-issue-filing`.

## How to Inspect the Diff
Linked worktree — inspect the uncommitted working tree, not `git diff main...HEAD`:
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend
git status --porcelain
git diff tests/test_work_id_nesting.py tests/test_crew_delivery_addressing.py
```
The episode fix is NOT a git diff on an existing tracked file in the usual sense —
`episodes/active/epic-567-door_cmdr-b-003.md` is modified in place by the `restate-assertion`
writer (the only legitimate write path); inspect it with `git diff episodes/active/epic-567-door_cmdr-b-003.md`
and confirm the history line at the bottom of assertion `a5` carries the ORIGINAL statement
verbatim (never edited/lost), per `EPISODE_STORE.md`'s contract.

## Task Statement
Fix exactly the 3 named tests (group 1) and the 1 named episode assertion (group 2) the
Admiral diagnosed as net regressions against `main` on PR #621, without weakening
`ExternalBackend.verify()`'s default-refuse behavior and without touching group 3
(map/INDEX.md, explicitly withdrawn).

## Close Criteria
- `tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_flat_work_id_finalizes_identically` passes.
- `tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_nested_work_id_finalizes_its_own_registry` passes.
- `tests/test_crew_delivery_addressing.py::JobAddressedDeliverySurvivesRelaunch::test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity` passes.
- `tests/test_episode_observations.py::RealStoreTests::test_the_real_store_is_clean_under_strict` and
  `::test_the_real_store_scan_actually_examined_the_records` pass.
- `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
  is CONFIRMED STILL RED — this is a pass condition for this review, not a defect; flag as
  BLOCK only if `map/INDEX.md` was actually touched by this gate's diff (it must not be).
- `git diff episodes/active/epic-567-door_cmdr-b-003.md` shows only assertion `a5`'s
  `statement` line changed plus one new appended history line carrying the ORIGINAL text
  verbatim — no other assertion, no lifecycle-standing, no other field touched.
- No production code (`scripts/run_crew.py`) touched.
- `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py` untouched (fenced, lane A).
- Full suite check: `pytest tests/test_work_id_nesting.py tests/test_crew_delivery_addressing.py tests/test_episode_observations.py tests/test_crew_launcher.py -q`
  is fully green (no failures at all in this set).

## Allowed Scope
`tests/test_work_id_nesting.py`, `tests/test_crew_delivery_addressing.py`,
`episodes/active/epic-567-door_cmdr-b-003.md` (via the `restate-assertion` writer only —
never hand-edited), `.agent-work/567-b/triage-candidates/tc3-*.md` (new file).

## Specific Exclusions
- `map/INDEX.md` — must be untouched (withdrawn group 3). Flag as BLOCK if modified.
- `scripts/run_crew.py`, `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
  `tests/test_crew_launcher.py`, `tests/test_code_map.py` — must be untouched.

## Constraints the Implementation Must Respect
- `accept_mtime_only_risk` reason strings must honestly name what each test actually
  proves — not a generic "no spine given."
- The episode fix must go through `apply_episode_delta.py`'s `restate-assertion` op, never
  a hand-edit of the `.md` file.

## Map Anchors (inbound)
- **Structural:** `scripts/run_crew.py:verify_external_result` (read-only, its
  `accept_mtime_only_risk` kwarg from g1/PR #621), `tests/test_work_id_nesting.py:CrewRegistryAddressingTests._verify_round_trip`,
  `tests/test_crew_delivery_addressing.py:JobAddressedDeliverySurvivesRelaunch`.
- **Decision anchors:** `decision:and-not-rescue-semantics`,
  `decision:default-refuse-not-default-warn` (g1 MISSION_FRAME.md) — confirm these two
  test fixes exercise, not relitigate, the refusal.
  `@grade: settled/measured · leans g2-review`

## Evidence Produced
See `.agent-work/epic-567-door/cmdr-b/crew-handoffs/g2-implement-implementer-result.md` in
full: RED/GREEN for both call sites, full-file run (32 passed), g1's suite unaffected (217
passed). The Commander separately fixed the episode wording and confirmed
`test_episode_observations.py` (20 passed/2 subtests) and the map freshness test (still
red, as required) directly — reproduce at least the episode-guard result and the map test's
continued redness yourself rather than trusting the Commander's claim alone.

## Suggested Model Tier
simple bounded — two one-line test edits plus one episode-store restate op, exact fix
already specified by the Admiral.

## Stop Conditions
Stop and return BLOCK if: `map/INDEX.md` was touched; `scripts/run_crew.py` was touched;
the episode fix used anything other than `restate-assertion`; any of the 5 target tests
(3 group-1 + 2 group-2) is not actually green in your hands; the map freshness test is
unexpectedly green (would mean group 3 was silently done anyway, contradicting the
Admiral's explicit instruction to leave it red).

## Return Format
Return REVIEW_RESULT to
`.agent-work/epic-567-door/cmdr-b/crew-handoffs/g2-reviewer-result.md` before ending your
turn.

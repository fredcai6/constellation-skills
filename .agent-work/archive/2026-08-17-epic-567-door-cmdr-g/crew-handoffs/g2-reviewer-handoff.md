# Reviewer Handoff

## Gate
`g2` — reap + child-plan release (the #552 mechanism). Gate 2 of 3; g1 (verify+close primitives) is already reviewed and integrated; g3 composes `finish_work`.

## Survey State Location
Create your review survey checklist at `.agent-work/epic-567-door/cmdr-g/g2-review/review.json`.

## What Was Implemented
Two new functions in `scripts/spine_lifecycle.py`, plus tests:
- `force_reap(project_dir) -> dict | None` — a two-line library call into `spine_rail._binding_transaction(project_dir, lambda reaped: reaped)`, forcing an immediate persist of the already-reaped binding map instead of waiting for a future unrelated session's touch. Zero edits to `spine_rail.py`.
- `_release_child_plans(spine_path, work_dir, *, root, reason) -> dict` returning `{"released": [...], "unclaimed_active": [...]}`. Identifies child plans structurally (a JSON file whose realpath is strictly inside `work_dir` AND which some task in the parent spine names via `child_checklist`), releases each as an explicit forced non-owner (`--force --reason`, never echoing the child's own `session_id`), and refuses any candidate whose realpath escapes `work_dir` (symlink-safe).

Plus 9 new tests (95 → 104): 2 for `force_reap`, 7 for `_release_child_plans` including three negative tests (outside-`work_dir` spine untouched, unclaimed active JSON left alone and reported, symlink escape refused).

## How to Inspect the Diff
Uncommitted working tree in `/home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease`. `git status --porcelain` then `git diff -- scripts/spine_lifecycle.py tests/test_spine_lifecycle.py`.

## Task Statement
Add the two reap/child-release functions per `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g2-implementer-handoff.md` — the three safety properties (lineage not proximity, honest non-owner release, realpath escape refusal) are the actual gate; a version that works on the happy path but drops any of them fails review.

## Close Criteria
- `force_reap` calls `spine_rail._binding_transaction` with an identity mutate; no edit to `spine_rail.py`.
- `_release_child_plans` implements all three safety properties as **shipped code**, not just tested behavior — read the function body, not just the tests.
- Child releases go through g1's `_engine_call` with `--force --reason`, never by reading and echoing a child's own `session_id` back as the caller id. Verify this yourself: `grep -n "def _release_child_plans" -A 80 scripts/spine_lifecycle.py` and confirm no `child_session.get("session_id")`-shaped read feeds into a `release` call's `--session-id` argument.
- The 3 negative tests are real and load-bearing — re-run them individually and read what they actually assert (not just that they pass): outside-`work_dir` spine untouched, unclaimed active JSON left alone AND reported in `unclaimed_active`, symlink escape refused with the real target's lease surviving.
- `force_reap`'s immediacy is genuinely tested (binding entry gone right after the call, not eventually) — re-run and confirm the fixture's target really reads `released` before `force_reap` runs (the precondition the reap depends on).
- Fenced files empty diff: `git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py`.
- `checklist_engine.main` appears exactly once in the module (inside `_engine_call`, from g1) — `_release_child_plans` must route through `_engine_call`, never call `checklist_engine.main` or `subprocess` directly.
- Full suite green.

## Allowed Scope
`scripts/spine_lifecycle.py` (the two functions), `tests/test_spine_lifecycle.py` (their tests/fixtures/helpers).

## Specific Exclusions
`scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `scripts/hooks/spine_rail.py` — must show empty diff. `done_refusal`/`_engine_call`/`_advance_and_release` (g1) must be unchanged — reuse only. `finish_work`, `open_pr`, the CLI are g3 — their absence here is expected, not a defect.

## Constraints the Implementation Must Respect
- Never run against a live spine file — `force_reap`'s tests must build fixtures under `tmp_path`, never point at this repo's real `.agent-work/.spine-rail-binding.json` or any live spine.
- `_release_child_plans`'s `work_dir` containment check must be realpath-based (`Path.resolve()` + `is_relative_to`), not string-prefix matching.

## Map Anchors (inbound)
- **Structural:** `scripts/hooks/spine_rail.py` — `_reap_binding_entries` (:311-366), `_binding_transaction` (:397-436) — read-only. `scripts/spine_lifecycle.py` — `_active_engine_session_spine` (:180) for contrast (a different, proximity-based question).
- **Capability:** immediate binding-store reap; child-plan lease release (#552's mechanism half).
- **Decision anchors:** `decision:child-plans-count` — the archive step must release child plans' leases too, not just the top-level spine.
  `@grade: settled/issue · leans g2-implement,g3-implement`
- **Evidence expectations:** `_reap_binding_entries` only drops entries whose target reads `status == "released"` — confirm the `force_reap` test's fixture genuinely satisfies that precondition rather than assuming the reap is unconditional.

## Evidence Produced
See `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g2-implementer-result.md` in full (thorough: all 3 negative tests pasted with output, an AST-scoped check that no child `session_id` is read for the caller id, pre/post counts). The Commander independently re-ran the full suite (104 passed), the fenced-file diff (empty), and a grep for `session_id` inside `_release_child_plans` before dispatching you. Re-verify independently rather than trusting either account.

## Suggested Model Tier
Sonnet — bounded; the three safety properties are mechanically checkable against the source and the negative tests.

## Stop Conditions
BLOCK if: any of the three safety properties is missing or weakened in the shipped code (not just under-tested); a fenced file shows non-empty diff; a child's own `session_id` is read and used as the release caller id anywhere; the suite is not green.

## Return Format
Return `REVIEW_RESULT` to `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g2-reviewer-result.md` before ending your turn.

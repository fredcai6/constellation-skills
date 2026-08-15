# Reviewer Handoff

## Gate

`g1-review`

## Survey State Location

`.agent-work/epic-568-530/g1-review/review.json`

## What Was Implemented

Commit `97eb5d34` adds a lexical `_worktree_from_spine(abs_spine)` helper and
uses it at the claim and SessionStart binding writers. It adds negative helper
cases and a real main-plus-linked-worktree regression.

## How to Inspect the Diff

Run `git show --format= 97eb5d34 -- scripts/hooks/spine_rail.py
tests/test_spine_rail.py`, inspect the implementer result at
`.agent-work/epic-568-530/crew-handoffs/g1-implement-implementer-result.md`,
and run the focused suite yourself. Source/test changes are committed; work
area artifacts are intentionally local-only.

## Task Statement

Ensure a binding for a resolved child spine records its owning linked worktree,
not stale hook payload cwd, without changing release semantics or #441 scope.

## Close Criteria

- APPROVE only if the helper accepts exactly absolute
  `.agent-work/<work-id>/<name>.json` paths and never falls back to cwd.
- Verify both claim and unambiguous SessionStart writers use it.
- Verify the real topology shares session, uses distinct agent ids and stale
  main cwd, does not inject the child path, and proves claim/Stop/release/
  SessionStart behavior.
- Verify parent Stop blocks only while its own parent binding is active, then
  becomes non-blocking while child remains active and foreign.
- Re-run `python -m pytest -q tests/test_spine_rail.py`.

## Allowed Scope

Review only `scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py` in
commit `97eb5d34`.

## Specific Exclusions

Flag any change to release target resolution, binding schema, locking, identity,
reaping, lifecycle policy, or #441 behavior.

## Constraints the Implementation Must Respect

- `abs_spine` is the sole ownership source.
- Invalid/out-of-layout attribution binds nothing; it never trusts stale cwd.
- No #441 expansion.

## Map Anchors (inbound)

- **Structural:** `README.md` declared degraded-map substitute.
- **Capability:** binding records identify a resolved spine's owning worktree.
- **Constraint:** resolved abs_spine is the ownership source; payload cwd is
  not.
- **Decision anchors:** resolved-spine-owns-worktree.
  @grade: settled/measured · leans g1-implement
- **Decision anchors:** no-441-expansion.
  @grade: settled/human · leans g1-implement
- **Evidence expectations:** real linked-worktree regression and focused rail
  suite.

## Evidence Produced

Record per-check findings, reviewer suite output, and a clear APPROVE/BLOCK
verdict for `g1-integrate.c2`.

## Suggested Model Tier

`stronger` — review must reject a plausible but non-discriminating worktree
test and detect forbidden store/lifecycle expansion.

## Stop Conditions

Return BLOCK if independent verification fails or a decision outside #530's
authority is needed.

## Return Format

Write `REVIEW_RESULT` to
`.agent-work/epic-568-530/crew-handoffs/g1-review-reviewer-result.md` before
ending, with verdict, per-check findings, blockers, out-of-scope observations,
and workflow feedback.

# Reviewer Handoff

## Gate
`g0-fix321-review` (issue-309, worktree C:/Programs/constellation-skills-wt/e298-309, branch epic-298/309)

## Survey State Location
`.agent-work/issue-309/g0-fix321-review/review.json`

## What Was Implemented
A fix for issue #321: `resolve_episode_path(episode_id, root)` in
`scripts/apply_episode_delta.py` (currently line ~733 after the change) now checks
`if not ID_RE.fullmatch(episode_id): return None` as its FIRST statement, before any
filesystem access. Previously it built `root / sub / f"{episode_id}.md"` from a
caller-handed id with zero format validation, so a crafted `..`-traversal id could
resolve outside `episodes/` entirely. One new adversarial test class,
`PathTraversalGuardTests`, was added to `tests/test_episode_store.py`.

## How to Inspect the Diff
This is an **uncommitted working tree** change in this worktree — use
`git status --porcelain` then `git diff -- scripts/apply_episode_delta.py
tests/test_episode_store.py` (not `git diff main...HEAD`, which would show unrelated
merged history). Full detail with the exact diff and new test source is also in
`.agent-work/issue-309/g0-fix321-implement/IMPLEMENTER_RESULT.md`.

## Task Statement
Add an `ID_RE.fullmatch(episode_id)` guard as the first check inside
`resolve_episode_path()`, returning `None` for a malformed id before any filesystem
check, fixing #321 at the one seam every id-taking reader routes through. Add one
adversarial test PROVING the guard fires (not merely that a lookup returns `None`,
since a well-formed-but-absent id already returned `None` before the fix too — a test
that only checks that would be a check that cannot fail).

## Close Criteria
- `resolve_episode_path()` returns `None` for any `episode_id` not matching `ID_RE`,
  without any filesystem access for that id.
- All existing behavior for well-formed ids unchanged.
- The new test demonstrates BOTH halves: (1) the exposure — a raw pre-fix-style path
  join, constructed inline in the test, resolving to a REAL file that actually exists
  on disk, not a hypothetical; (2) the fix — the real `resolve_episode_path()` (and
  `fetch_episode()`) refusing that same id post-fix. **Independently reproduce both
  halves yourself** — do not accept the IMPLEMENTER_RESULT's pasted output as proof;
  re-run the test, and separately, in a fresh Python REPL/script, confirm the claimed
  traversal target (`SKILL_INDEX.md` at repo root) really exists and that the raw
  pre-fix-style join really does resolve to it.
- `ID_RE`'s own pattern was not modified (`grep -n "^ID_RE" scripts/apply_episode_delta.py`
  should show it unchanged from `r"[a-z0-9][a-z0-9-]*-[0-9]{3,}"`).
- Full `tests/test_episode_store.py` suite green, net +1 test vs. the pre-change
  baseline (105 passed, 1 skipped -> claimed 106 passed, 1 skipped), 0 regressions.

## Allowed Scope
`scripts/apply_episode_delta.py` (`resolve_episode_path()` only) and
`tests/test_episode_store.py` (one new test class/function).

## Specific Exclusions
`query_episodes.py`, `episode_id_for()`, `iter_episode_ids()`, `docs/EPISODE_STORE.md`
were all out of scope for the implementer — flag if touched.

## Constraints the Implementation Must Respect
- No new exception type; `None` is the module's established "not found" contract.
- The fix lands at the ONE seam (`resolve_episode_path()`), not duplicated at each
  caller — verify no other call site in `scripts/*.py` was also touched
  (`grep -rn "resolve_episode_path(" scripts/*.py` should show only the one
  definition-site change plus the same two pre-existing call sites).

## Map Anchors (inbound)
- **Structural:** `apply_episode_delta.py resolve_episode_path()`
- **Capability:** episode store fetch/retrieval path
- **Constraints/assumptions:** #321 — the store validates ids it lists but not ids it is handed
- **Decision anchors:** `decision:fix-321-at-the-seam — bounded, single-function fix, no caller changes`
  `@grade: settled/measured · leans g0-fix321-implement`
- **Evidence expectations:** adversarial test proving the guard fires, not just "returns None"

## Evidence Produced
See `.agent-work/issue-309/g0-fix321-implement/IMPLEMENTER_RESULT.md` for the full diff,
new test source, and pasted pytest transcripts (baseline 105/1 skipped -> RED (new test
alone fails pre-fix, via a half-retired-guard exception rather than the originally
anticipated wrong-Path shape — read the "Note on this RED shape" paragraph in that file
and judge whether the substitute proof is still sound) -> GREEN 106/1 skipped).

## Suggested Model Tier
Simple bounded — one function, one test class, narrow diff.

## Stop Conditions
Stop and return BLOCK if: the diff is not what IMPLEMENTER_RESULT claims, the guard does
not actually fire when you test it yourself, the traversal target does not really exist,
the test would pass even without the guard (i.e. it's a check that cannot fail after
all), or the suite is not actually green when you run it yourself.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers,
out-of-scope observations, workflow feedback.

# Reviewer Handoff

## Gate
g3 (g3-review)

## Survey State Location
`.agent-work/w2-reindex/g3-review/review.json`

## What Was Implemented
The mission's own acceptance test: `tests/test_code_map_precommit_e2e.py` (7 test methods covering
all 8 numbered cases — real subprocess `git`, real installed hook, real scratch `git worktree add`
topology sharing one `.git`, never `git clone` per-worktree). Plus a Commander-run mechanical
`python -m scripts.code_map build --root .` that refreshed this repo's own `map/INDEX.md` (6 lines;
`map/ids.jsonl` unchanged), which was stale from gate 2's own tracked-file edits and was blocking
the full suite — unrelated to gates 1-3's shipped mechanism, root-caused correctly by the
implementer's attempt-2, fixed by the Commander (mechanical, outside this gate's `tests/`-only
scope), re-verified green by attempt-3.

## How to Inspect the Diff
Uncommitted working tree in `/home/tommy/projects/569-w2-reindex` — `git status --porcelain` then
`git diff`. This gate's own diff: `tests/test_code_map_precommit_e2e.py` (new) plus
`map/INDEX.md` (Commander's rebuild, not this gate's code but part of what makes the suite green —
confirm it is *only* an entity-count refresh, not a hand-edit). `scripts/code_map/`,
`scripts/hooks/`, `scripts/install_constellation.py`, `tests/test_install_constellation.py`,
`tests/test_code_map_precommit.py` are gates 1-2's already-approved diff — present but not this
gate's to re-review.

## Task Statement
Prove gates 1-2's shipped code works end to end against real scratch git repos: hook fires on a
real `git commit`, fixes stale map silently, true no-op when fresh, both partial-commit shapes for
real, fires from a second worktree sharing the same `.git` (this repo's real dev topology), and
`MapTreeFreshnessTests` stays the exact backstop it was, unmodified. Full original task in
`.agent-work/w2-reindex/crew-handoffs/g3-implement-handoff.md`; the case list there is authoritative.

## Close Criteria
- Every scratch setup uses `git worktree add` against one shared scratch `.git` (via `git clone
  --bare` of THIS repo's own common `.git`, done once, then `git worktree add` off it) — **never a
  second `git clone` per worktree**, which would defeat case 7's whole point. Check this directly
  in the test file's fixture helpers.
- All 8 numbered cases from the original handoff are genuinely covered by the 7 test methods (case
  2/3 combined into one method — check this is a deliberate combination, not a dropped case).
- `git diff -- tests/test_code_map.py` empty.
- Full local suite: `0 failed`, pass count at/above `3622 passed, 6 skipped, 0 failed` plus this
  plan's added tests.
- The red proof (case 1) is pinned to a SHA that is actually this branch's HEAD at gate-close time —
  confirm `git rev-parse HEAD` still matches `9d5aac6d` (or whatever it is by the time you review) and
  that the test file's `PINNED_SHA_PREFIX` matches it.

## Allowed Scope
`tests/test_code_map_precommit_e2e.py` only (new file). The Commander's `map/INDEX.md` rebuild is a
separate, already-explained mechanical action — verify it is correct (matches a fresh
`python -m scripts.code_map build --root .` output) but it is not this gate's implementation to
critique as if a crew wrote it.

## Specific Exclusions
`scripts/code_map/`, `scripts/hooks/`, `scripts/install_constellation.py` — gates 1-2's code,
already approved; flag as a BLOCK only if THIS gate's diff modifies them (it should not).
`generate_spine.py`, `specs/`, `scripts/checklist_engine.py`, any shipped spine template.

## Constraints the Implementation Must Respect
- **Independently re-verify, not just re-read**: re-run the red proof (case 1) and the
  second-worktree case (case 7) yourself against a fresh scratch worktree — these are the two claims
  most costly to accept on trust, since they are what makes this gate's evidence genuine end-to-end
  proof rather than a repeat of gates 1-2's unit-level claims.
- Confirm no case substitutes `git clone` where a shared-`.git` `git worktree add` was required —
  read every fixture helper, not just the docstrings.
- Confirm the `map/INDEX.md` rebuild is exactly what a fresh build produces — run
  `python -m scripts.code_map build --root /tmp/scratch-map-check --artifacts /tmp/... --out
  /tmp/...` style comparison yourself if you want independent confirmation, or diff against
  `git show HEAD:map/INDEX.md` reasoning — do not just trust the implementer's line-count claim.

## Map Anchors (inbound)
- **Structural:** this checkout's own `git worktree list` (the required topology for case 7),
  `tests/test_code_map.py::MapTreeFreshnessTests` (the backstop both this gate's proof and the
  regression check exercise).
- **Constraints/assumptions:** must-be-installed-not-merely-built (hard, proven here);
  do-not-weaken-the-freshness-test (hard, proven unmodified here); red-proof pinned to shipped
  revision (launch order standing pre-ruling) — verify the pin is still accurate at review time.
- **Decision anchors:** N/A — no new decision at this gate, pure proof.

## Evidence Produced
From `IMPLEMENTER_RESULT` (attempt-2, the substantive work) and attempt-3 (pure re-verification
after the Commander's map rebuild): `python -m pytest tests/test_code_map_precommit_e2e.py -q` → 7
passed. Full suite → `3656 passed, 6 skipped, 0 failed`, `1275 subtests passed`. `git diff --
tests/test_code_map.py` empty. `git diff --stat -- map/INDEX.md map/ids.jsonl` → only the
Commander's 6-line rebuild on `map/INDEX.md`. This evidence targets `g3-integrate.c1`.

## Suggested Model Tier
stronger — reason: independently re-executing real subprocess git orchestration (not just reading
code) across multiple scratch worktrees is the whole point of this review; it rewards care.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, any case
substitutes `git clone` for the required shared-worktree topology, the red-proof pin is stale, or a
policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT (verdict APPROVE or BLOCK) to
`.agent-work/w2-reindex/crew-handoffs/g3-review-reviewer-result.md` before ending your turn.

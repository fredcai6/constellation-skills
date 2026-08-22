# Reviewer Handoff

## Gate
`g1` (work-id `w1-verdict`, epic 569, issue #371)

## Survey State Location
`.agent-work/w1-verdict/g1-review/review.json`

## What Was Implemented
`scripts/checklist_engine.py`'s two `match`-comparison sites (`_check_condition`'s artifact
branch, `attest`'s artifact branch) now share one comparator helper (`_artifact_match_satisfied`)
that treats a list-valued `match[k]` as membership (`have in want[k]`) while every scalar
`match[k]` keeps `==` unchanged. A present-but-non-`dict` `match` is now a clean refusal at both
sites (`satisfied=False` / `EngineError`) instead of the prior uncaught `AttributeError` on
`.items()`. `scripts/validate_spine.py` gained a blocking shape fault
(`shape-artifact-match-not-dict`) for the non-dict case, a report-only falsifiability fault
(`falsifiable-artifact-malformed-match-list`) for an empty or non-scalar-element list value, and a
new `ValidationResult.report_only` channel + `REPORT_ONLY_FAULT_CODES` set that routes the new
fault so it can never affect `bool(result)`/exit code at either existing caller
(`generate_spine.py`, `spine_lifecycle.py`). `docs/CHECKLIST_SCHEMA.md` gained one clause on the
`artifact` row.

## How to Inspect the Diff
Uncommitted working tree in this worktree (`/home/tommy/projects/569-w1-verdict`, branch
`epic-569/w1-verdict`): `git status --porcelain` then `git diff` — 5 tracked files touched
(`scripts/checklist_engine.py`, `scripts/validate_spine.py`, `docs/CHECKLIST_SCHEMA.md`,
`tests/test_checklist_engine.py`, `tests/test_validate_spine.py`); `.agent-work/w1-verdict/` is
this run's own untracked workbench, not part of the reviewed diff.

## Task Statement
Widen the `match` comparator to accept "any of these acceptable values" (a list-valued
`match[k]`, membership) without breaking any existing scalar `match`, and make `validate_spine.py`
refuse (report-only, named promotion trigger) a mistyped `match` shape — issue #371, epic 569 wave
1. `APPROVE-WITH-FOLLOWUPS`/verdict-vocabulary work is explicitly OUT of scope
(`decision:371-vocabulary-half-is-already-done`) and must not appear in the diff.

## Close Criteria
- Both comparator sites use one shared helper; scalar `match` behavior is provably unchanged
  (backward-compat corpus proof, both hit and miss cases for every existing shipped scalar
  `match`).
- A list-valued `match[k]` is membership (`have in want[k]`); verify against a case not in the
  shipped corpus (e.g. `{"verdict": ["APPROVE", "BLOCK"]}`).
- A present-but-non-`dict` `match` no longer crashes at either site (reproduce the pre-change
  `AttributeError` is NOT reachable post-change).
- `validate_spine.py`'s new shape fault (non-dict match) is blocking; its new falsifiability fault
  (malformed list) is report-only and demonstrably cannot flip `bool(result)`/exit code — check
  BOTH existing `validate()` callers (`generate_spine.py:1043`, `spine_lifecycle.py:396,454`) test
  only base-list truthiness, never `.report_only`.
- The promotion trigger for the report-only fault is stated verbatim as a code comment beside
  `REPORT_ONLY_FAULT_CODES` in `scripts/validate_spine.py`, and is a genuinely actionable
  measurement (not vague).
- `docs/CHECKLIST_SCHEMA.md`'s `artifact` row is ADDED to, not rewritten.
- Full local `pytest -q` — every failure outside `tests/test_code_map.py::MapTreeFreshnessTests
  ::test_map_tree_freshness_root_index_matches_a_fresh_build` is a BLOCK; that one specific test is
  a documented pre-existing failure at base commit `244665ee0f669a0bb23847c8fa695c430910c06d`
  (map is stale, unrelated to this diff) — reproduce it yourself at that commit (e.g. `git stash` /
  checkout) rather than trusting the claim.

## Allowed Scope
`scripts/checklist_engine.py`, `scripts/validate_spine.py`, `docs/CHECKLIST_SCHEMA.md`,
`tests/test_checklist_engine.py`, `tests/test_validate_spine.py`.

## Specific Exclusions
- `scripts/hooks/`, `waive()`'s `produced_by`/`override_policy.authority` (#557), any new
  `scripts/verify_*.py`/`scripts/check_*.py` script, `APPROVE-WITH-FOLLOWUPS`/verdict vocabulary,
  and any `skills/*/templates/*.json` or `.agent-work/templates/` edit — flag as BLOCK if any of
  these appear touched in the diff.

## Constraints the Implementation Must Respect
- Every existing scalar `match` in the shipped corpus keeps behaving identically
  (`decision:backward-compatibility-is-non-negotiable`).
- The widening ships live; the new `validate_spine` refusal ships report-only with a named
  promotion trigger (`decision:widening-ships-live-refusal-ships-report-only`).

## Map Anchors (inbound)
map/INDEX.md and map/ids.jsonl are DEGRADED-UNPARSEABLE at this commit (also independently
reproduced: `tests/test_code_map.py`'s freshness test fails identically at the base commit) — no
map entry point exists to hand down.
- **Structural:** `scripts/checklist_engine.py:_check_condition` (artifact branch, ~1080-1112,
  now delegating to `_artifact_match_satisfied` at ~1036), `scripts/checklist_engine.py:attest`
  (artifact branch, ~3450-3463), `scripts/validate_spine.py:_shape_task_faults` (new inline
  non-dict-match check), `scripts/validate_spine.py:_fault_artifact_malformed_match_list` (new),
  `scripts/validate_spine.py:ValidationResult` (new `.report_only` channel).
- **Capability:** engine `artifact`-postcondition match comparison; `validate_spine`'s
  falsifiability fault family.
- **Constraints/assumptions:** `decision:backward-compatibility-is-non-negotiable`,
  `decision:widening-ships-live-refusal-ships-report-only`.
- **Decision anchors:**
  - `decision:match-shape-bare-list` — list-valued `match[k]` means membership.
    `@grade: settled/admiral · leans g1-implement,g1-review`
  - `decision:match-not-dict-is-shape-fault` — blocking shape fault, not the report-only family.
    `@grade: settled/admiral · leans g1-implement,g1-review`
  - `decision:malformed-list-definition` — empty or non-scalar element is malformed; single-element
    list is NOT flagged.
    `@grade: settled/admiral · leans g1-implement,g1-review`
  - `decision:promotion-trigger` — named verbatim as a code comment.
    `@grade: settled/admiral · leans g1-implement,g1-review`
- **Evidence expectations:** red/green comparator proof pinned to a commit SHA; corpus
  backward-compat proof; validate_spine positive tests; full suite.
- **Map confidence flags:** map DEGRADED — noted above, does not block this review.

## Evidence Produced
See `.agent-work/w1-verdict/crew-handoffs/g1-implement-implementer-result.md` (full
`IMPLEMENTER_RESULT`) — Evidence sections 1-5: red/green comparator proof, non-dict-match
before/after proof, corpus backward-compat proof (4 cases), `validate_spine` positive tests (2
standalone dict constructions), full-suite output (`1 failed, 3592 passed, 6 skipped`, the 1
failure named and reproduced as pre-existing at base). Target postcondition for your verdict:
`g1-integrate.c2` (`review-result` match `verdict: APPROVE`).

## Suggested Model Tier
simple bounded — small, fully specified diff; verification is mechanical (re-run the pasted
commands, read the two diffs, confirm no scope creep).

## Stop Conditions
Stop and return BLOCK if: the diff touches any Specific Exclusion, a claimed evidence figure does
not reproduce when you re-run it, the pre-existing test failure claim does not reproduce at the
base commit, or any existing scalar-match corpus case now resolves differently than before.

## Return Format
Return `REVIEW_RESULT` to
`.agent-work/w1-verdict/crew-handoffs/g1-review-reviewer-result.md` before ending your turn.

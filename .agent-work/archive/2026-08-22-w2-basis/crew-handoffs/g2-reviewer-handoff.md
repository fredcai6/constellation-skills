# Reviewer Handoff

## Gate
g2 (g2-review)

## Survey State Location
Create your review survey checklist at `.agent-work/w2-basis/g2-review/review.json`.

## What Was Implemented
A `basis` field (g1's already-shipped mechanism) hand-authored onto exactly three conditions — `plan.c2`, `plan.c4`, `plan.c5` — in the shipped `skills/commander/templates/COMMANDER_SPINE.template.json`, plus the `.agent-work/templates/` overlay + baseline copies synced, plus a new red-proof integration test class (`CommanderSpineBasisFields`) pinned to shipped HEAD (`9d5aac6daa58a72fc6a665cb39879ee5705f7f71`). Full implementer account: `.agent-work/w2-basis/crew-handoffs/g2-implementer-result.md`.

## How to Inspect the Diff
Uncommitted working tree in this worktree (`/home/tommy/projects/569-w2-basis`) — `git status --porcelain` then `git diff`. Expect exactly 4 files touched: the shipped template, its two overlay copies, and `tests/test_checklist_engine.py`.

## Task Statement
Author `basis` on exactly `plan.c2`/`plan.c4`/`plan.c5`, matching the shapes ratified in `.agent-work/w2-basis/PLAN_ALTERNATIVES.md`, without touching any other condition, and prove it with a real-file integration test.

## Close Criteria
- `git diff skills/commander/templates/COMMANDER_SPINE.template.json` touches ONLY `plan.c2`, `plan.c4`, `plan.c5` — confirm by reading the diff line-by-line, not by trusting the implementer's own count.
- Each of the 3 `basis` objects has `locator_kind: "file"` and a `locator.path` matching what's specified in `PLAN_ALTERNATIVES.md`/g2's handoff (`.agent-work/<work-id>/execute.json` for c2; glob `plan-candidate-*.md` min 2 matches for c4; `PLAN_CRITIC.md` for c5) — verify the JSON is well-formed (not just "looks right") by loading it with `json.load` yourself.
- `<work-id>` remains an unresolved literal placeholder in the shipped file (this template is instantiated per-run) — flag as a BLOCK if it was accidentally resolved to `w2-basis`.
- The shipped template, `.agent-work/templates/COMMANDER_SPINE.template.json`, and `.agent-work/templates/.baseline/constellation-commander/COMMANDER_SPINE.template.json` are byte-identical — verify with `diff`, don't trust the claim.
- The new `CommanderSpineBasisFields` test class is genuinely pinned to a shipped revision (reads `git rev-parse HEAD` or an equivalent, and has a real skip/fail path if HEAD has moved) — inspect the test source, not just its pass/fail.
- The new test's red-proof is real: independently reproduce it (stash the template edit, rerun `-k CommanderSpineBasisFields`, confirm failures, restore, rerun, confirm green) rather than trusting the pasted transcript.
- Full `tests/test_checklist_engine.py` suite passes with exactly +3 tests / +3 subtests over g1's baseline (511/145 → 514/148) — reproduce the exact numbers yourself.
- `GoldenOutputBriefing`/`TemplateOnlyFieldAllowlist` still pass — this is the FIRST time g1's render code runs against real shipped content (a real `basis` field in a real template, not a test fixture), so this is a meaningful check, not a formality.
- No other file in the repo changed.

## Allowed Scope
`skills/commander/templates/COMMANDER_SPINE.template.json`, `.agent-work/templates/COMMANDER_SPINE.template.json`, `.agent-work/templates/.baseline/constellation-commander/COMMANDER_SPINE.template.json`, `tests/test_checklist_engine.py` (new test class only).

## Specific Exclusions
`scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md` (g1's scope, already shipped), any condition in the template other than `plan.c2/c4/c5`, `generate_spine.py`/`specs/`.

## Constraints the Implementation Must Respect
Surgical text edit only (no `json.load`/`json.dump` round-trip of the template — check this by looking at whether unrelated lines/formatting shifted anywhere in the diff, which would be the tell-tale sign of an accidental round-trip).

## Map Anchors (inbound)
- **Structural:** `skills/commander/templates/COMMANDER_SPINE.template.json:plan.c2/c4/c5`.
- **Constraints/assumptions:** `ruling-engine-first-backfill-where-it-earns-it` (exactly 3, not more) | `ruling-basis-lives-in-hand-written-templates` | `ruling-red-proof-pinned-to-shipped-revision`.
- **Decision anchors:** the 3 conditions + shapes are ratified in `.agent-work/w2-basis/PLAN_ALTERNATIVES.md`.
  `@grade: settled/human`

## Evidence Produced
Full IMPLEMENTER_RESULT at `.agent-work/w2-basis/crew-handoffs/g2-implementer-result.md`. Target postcondition for your verdict: `g2-integrate.c2` (reviewer verdict = APPROVE).

## Suggested Model Tier
simple bounded — reason: a narrow, mechanically-verifiable template diff; independent reproduction of the pytest counts and JSON parse is the bulk of the work.

## Stop Conditions
Return BLOCK if: any condition other than plan.c2/c4/c5 changed, the overlay copies drifted, `<work-id>` was resolved, the red-proof doesn't actually reproduce, or the pytest counts don't match exactly.

## Return Format
Return REVIEW_RESULT to `.agent-work/w2-basis/crew-handoffs/g2-reviewer-result.md` before ending your turn.

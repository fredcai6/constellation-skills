# Reviewer Handoff

## Gate
g5-implement (execute.json, work-id w3-promote) — reviewing the implementer's completed slice

## Survey State Location
Create your review survey checklist at `.agent-work/w3-promote/g5-review/review.json`.

## What Was Implemented
1 of 3 candidate `check: null` conditions in `skills/charter/templates/CHARTER.template.json`
promoted to a real `artifact`-kind check (no new engine mechanism): `project-templates.c1`, full
promotion, enum-match on `status` in `{"seeded", "skipped-no-need"}`, mirroring COMMANDER_SPINE's
already-landed `plan.c1` shape. `closeout.c1` and `interrogate.c1` were both fresh-verified and left
`check: null`: `closeout.c1`'s archive-path half has the same wall-clock-keyed-path defect g3
already declined for ADMIRAL_SPINE's `closeout.c4`; `interrogate.c1`'s candidate verifier
(`scripts/verify_interrogation.py`) exists but the cross-skill `<ROLE-skill-dir>` placeholder
resolver and `install_constellation.py`'s per-skill manifest don't actually wire it to `charter` (it
would silently break in an installed repo). Overlay synced byte-identical. A new red-proof test
class `CharterW3PromotePromotions` added to `tests/test_checklist_engine.py`.
`tests/test_validate_spine.py`'s floor updated 15→14 (a genuine all-null gate cleared — confirm
which gate).

## How to Inspect the Diff
Uncommitted working tree. `git status --porcelain` then `git diff` for each file below
(untracked-safe). The worktree also carries prior gates' already-committed work (g1, g3, g4 — do
not re-review); scope your diff inspection to the CHARTER-related files named below only.

## Task Statement
Promote the bucket-2 conditions in `skills/charter/templates/CHARTER.template.json` per
`notes-1.md`'s CHARTER section, using only existing engine check kinds
(`decision:no-new-check-kinds`), red-proof each with an adversary-chosen mutation, keep the suite
green at this gate boundary. Full handoff:
`.agent-work/w3-promote/crew-handoffs/g5-implementer-handoff.md`. Full result:
`.agent-work/w3-promote/crew-handoffs/g5-implementer-result.md`.

## Close Criteria
- Exactly 1 condition changed in `CHARTER.template.json` (`project-templates.c1`); `closeout.c1`,
  `interrogate.c1`, `orchestrator-context.c1`, `agent-guide.c1`, and every other condition in the
  file untouched — verify against `git diff`. `orchestrator-context.c1`/`agent-guide.c1` in
  particular must be confirmed unchanged (they already carry real checks; only their preconditions
  are null, which is gate-order-guaranteed and correctly out of scope).
- `project-templates.c1`'s shape matches what the handoff specified: `artifact` kind, enum-match on
  `status`, statement text unchanged.
- `artifact`-kind eligibility justified against THIS template's own pre-existing checks — spot-check
  the implementer's claim that other `artifact`/`user-decision` checks already exist in this file
  before this change (`git show HEAD:skills/charter/templates/CHARTER.template.json`).
- `closeout.c1`'s left-null disposition: independently verify the wall-clock-path claim against
  `scripts/spine_lifecycle.py` yourself (same check g3's reviewer already did for ADMIRAL_SPINE
  `closeout.c4` — does the same defect genuinely apply here, or is this pattern-matched without
  re-verifying?).
- `interrogate.c1`'s left-null disposition: independently verify `scripts/verify_interrogation.py`
  exists, and independently check the `<ROLE-skill-dir>` resolver
  (`scripts/init_work_area.py::_resolve_skill_dir_token`) and `install_constellation.py`'s manifest
  to confirm the implementer's claim that it isn't actually wired to `"charter"`. This is the kind
  of claim that's easy to accept on faith — read the actual source yourself.
- NO `basis` field anywhere in the diff (`decision:no-basis-backfill` — g4 got this wrong once
  already this wave; g5's implementer was warned explicitly and claims a clean diff — verify that
  claim: `grep -n "basis" skills/charter/templates/CHARTER.template.json` should return nothing new).
- Overlay (`.agent-work/templates/CHARTER.template.json`) byte-matches; confirm with
  `python3 scripts/check_template_overlay_freshness.py`.
- The red-proof test class: does it (a) assert the exact shipped shape, (b) assert no other
  condition in the file changed, (c) attack with a genuinely adversarial mutation (not a
  restatement of the check's own match text)?
- `tests/test_validate_spine.py`'s floor: independently re-run the corpus-wide
  `falsifiable-all-null` sweep pre/post-edit and confirm the 15→14 drop is real and correctly
  attributed to `project-templates` clearing (it had exactly one postcondition).
- Full suite green AFTER all of the above:
  `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q`.

## Allowed Scope
`skills/charter/templates/CHARTER.template.json`, `.agent-work/templates/CHARTER.template.json`,
`tests/test_checklist_engine.py` (new class only), `tests/test_validate_spine.py` (floor
numbers/message only). You are reviewing, not editing — BLOCK with specific findings if something
is wrong, do not fix it yourself.

## Specific Exclusions
Do not touch or re-review `COMMANDER_SPINE.template.json`, `ADMIRAL_SPINE.template.json`, or
`EXPLORER_SPINE.template.json` (already integrated). Do not touch `checklist_engine.py`.

## Constraints the Implementation Must Respect
- `decision:no-new-check-kinds` — only `artifact` used, verify no new kind invented.
- `decision:no-basis-backfill` — verify NO `basis` field survives anywhere in the diff.
- `decision:blocking-where-adjudicated` — the 1 promotion ships blocking; verify justified against
  THIS template's own pre-existing checks.
- Compact-format JSON hand-edit discipline — diff should be a single-line change, not reflowed.

## Map Anchors (inbound)
- **Structural:** `skills/charter/templates/CHARTER.template.json`.
- **Decision anchors:** `decision:no-new-check-kinds` `@grade: settled/human`;
  `decision:no-basis-backfill` `@grade: settled/human`;
  `decision:blocking-where-adjudicated` `@grade: settled/human`.

## Evidence Produced
See `g5-implementer-result.md`'s Evidence section. Independently reproduce every command rather
than trusting the pasted output.

## Suggested Model Tier
simple bounded — mechanical verification against a well-specified handoff, small diff.

## Stop Conditions
Return BLOCK if: the promoted check's shape diverges from spec without a stated, sound reason; a
`basis` field survives anywhere; the red-proof is not genuinely adversarial; the overlay is stale;
the full suite is not green; any excluded file was touched; `closeout.c1`'s or `interrogate.c1`'s
left-null reasoning does not hold up under your own independent source read.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback. Write to
`.agent-work/w3-promote/crew-handoffs/g5-reviewer-result.md` before ending your turn.

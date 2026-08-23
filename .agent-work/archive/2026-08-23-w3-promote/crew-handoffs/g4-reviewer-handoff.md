# Reviewer Handoff

## Gate
g4-implement (execute.json, work-id w3-promote) — reviewing the implementer's completed slice

## Survey State Location
Create your review survey checklist at `.agent-work/w3-promote/g4-review/review.json`.

## What Was Implemented
3 of 4 candidate `check: null` conditions in `skills/explorer/templates/EXPLORER_SPINE.template.json`
promoted to real `command`-kind checks (no new engine mechanism): `init.c2` (full promotion, mirrors
g1/g3's lease-claim seam), `context.c1` and `spec.c1` (SPLIT promotions — existence-only checks on
`IDEAS_BOARD.md`/`DESIGN_SPEC.md`; the judgment halves of their `statement` text stay unchecked).
`route.c1` was left `check: null` — no per-outcome routing artifact exists to discriminate the 3
named routing outcomes. Overlay synced byte-identical. A new red-proof test class
`ExplorerSpineW3PromotePromotions` added to `tests/test_checklist_engine.py`.
`tests/test_validate_spine.py`'s floor message updated (17→15, corpus-wide `falsifiable-all-null`
count) since `context`/`spec` each had exactly one postcondition and clearing it clears their gate.

**IMPORTANT — a Commander correction is already baked into what you're reviewing, read this
first:** the implementer's first pass added a `basis` object to `context.c1` and `spec.c1`, citing
COMMANDER_SPINE's `plan.c2/c4/c5` precedent. That precedent is real but belongs to a DIFFERENT
decision than the one authorizing it: `decision:no-basis-backfill` (this wave's own pre-ruling)
explicitly forbids rolling the `basis` field out across this wave's promotions — that mechanism is
reserved for a sibling lane (`w3-basis`), a different population. The Commander caught this and
stripped the `basis` objects before dispatching you, and corrected the test class's docstring and
one test method (`test_context_c1_and_spec_c1_keep_their_unsplit_statement_and_no_basis`, now
asserting `basis` is ABSENT). **Your job includes independently re-verifying this correction is
actually complete** — search the diff and the test file for any remaining `basis` reference tied to
this gate's conditions (docstring prose, test assertions, JSON) and confirm none survive. Also
independently confirm the underlying premise: is `decision:no-basis-backfill` genuinely being
violated by adding `basis` to a NEWLY promoted condition, or does the pre-ruling only bar something
narrower (e.g. bulk backfill across untouched conditions, not backfill onto a condition this same
wave is promoting)? Read the pre-ruling text yourself (LAUNCH_ORDER-w3-promote.md's Pre-Rulings
section, `decision:no-basis-backfill`) and form your own judgment — flag disagreement as a finding
rather than assuming the Commander's read is correct.

## How to Inspect the Diff
Uncommitted working tree. `git status --porcelain` then `git diff` for each file below
(untracked-safe). The worktree also carries prior gates' already-committed work (g1, g3 — do not
re-review); scope your diff inspection to the EXPLORER_SPINE-related files named below only.

## Task Statement
Promote the bucket-2 conditions in `skills/explorer/templates/EXPLORER_SPINE.template.json` per
`notes-1.md`'s EXPLORER_SPINE section, using only existing engine check kinds
(`decision:no-new-check-kinds`), red-proof each with an adversary-chosen mutation, keep the suite
green at this gate boundary. Full handoff:
`.agent-work/w3-promote/crew-handoffs/g4-implementer-handoff.md`. Full result (includes the
Commander Correction section):
`.agent-work/w3-promote/crew-handoffs/g4-implementer-result.md`.

## Close Criteria
- Exactly 3 conditions changed in `EXPLORER_SPINE.template.json` (`init.c2`, `context.c1`,
  `spec.c1`); `route.c1` and every other condition in the file untouched — verify against `git diff`.
- `init.c2` shape matches g1's/g3's landed lease-claim seam exactly.
- `context.c1`/`spec.c1`: existence-only `command` check, `statement` text byte-unchanged, NO
  `basis` field (see the Commander Correction note above — verify this thoroughly).
- `command`-kind eligibility justified against THIS template's own pre-existing (non-null) checks
  — spot-check the implementer's claim that `init.c1`, `explore.c2`, `review.c1`, `confirm.c2/c3`
  were already `command`-kind before this change (`git show HEAD:skills/explorer/templates/EXPLORER_SPINE.template.json`).
- `route.c1`'s left-null disposition: independently verify — is there really no tooling/artifact
  that discriminates the 3 named routing outcomes? Check the `skills/explorer/` tree and shared
  `scripts/` dir yourself rather than trusting the implementer's claim.
- Overlay (`.agent-work/templates/EXPLORER_SPINE.template.json`) byte-matches; confirm with
  `python3 scripts/check_template_overlay_freshness.py`.
- The red-proof test class: for each of the 3 promoted conditions, does it (a) assert the exact
  shipped shape, (b) assert no other condition in the file changed, (c) attack with a genuinely
  adversarial mutation (not a restatement of the check's own command text)? Read each
  discrimination test closely.
- `tests/test_validate_spine.py`'s floor: independently re-run the corpus-wide
  `falsifiable-all-null` sweep pre/post-edit and confirm the 17→15 drop is real and correctly
  attributed (context/spec clearing their gates, not some other cause).
- Full suite green AFTER all of the above:
  `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q`.

## Allowed Scope
`skills/explorer/templates/EXPLORER_SPINE.template.json`,
`.agent-work/templates/EXPLORER_SPINE.template.json`, `tests/test_checklist_engine.py` (new class
only), `tests/test_validate_spine.py` (floor message only). You are reviewing, not editing — BLOCK
with specific findings if something is wrong, do not fix it yourself.

## Specific Exclusions
Do not touch or re-review `COMMANDER_SPINE.template.json` or `ADMIRAL_SPINE.template.json` (g1's
and g3's, already integrated). Do not touch `checklist_engine.py`.

## Constraints the Implementation Must Respect
- `decision:no-new-check-kinds` — only `command` used, verify no new kind invented.
- `decision:no-basis-backfill` — verify NO `basis` field survives on any condition this gate
  touched (see the Commander Correction note above — this is the highest-priority thing to
  independently re-check in this review).
- `decision:blocking-where-adjudicated` — all 3 shipped blocking; verify justified per-condition
  against THIS template's own pre-existing checks.
- Compact-format JSON hand-edit discipline — diff should be a handful of single-line changes, not
  reflowed.

## Map Anchors (inbound)
- **Structural:** `skills/explorer/templates/EXPLORER_SPINE.template.json`.
- **Decision anchors:** `decision:no-new-check-kinds` `@grade: settled/human`;
  `decision:no-basis-backfill` `@grade: settled/human`;
  `decision:blocking-where-adjudicated` `@grade: settled/human`;
  `decision:red-proof-each-promotion` `@grade: settled/admiral`.

## Evidence Produced
See `g4-implementer-result.md`'s Evidence section and Commander Correction section. Independently
reproduce every command rather than trusting the pasted output.

## Suggested Model Tier
simple bounded — mechanical verification against a well-specified handoff, plus one specific
policy-compliance re-check.

## Stop Conditions
Return BLOCK if: any promoted check's shape diverges from spec without a stated, sound reason; a
`basis` field or any other trace of the corrected violation survives anywhere in the diff; the
red-proof for any condition is not genuinely adversarial; the overlay is stale; the full suite is
not green; any excluded file was touched; `route.c1`'s left-null reasoning does not hold up under
your own independent check.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback. Write to
`.agent-work/w3-promote/crew-handoffs/g4-reviewer-result.md` before ending your turn.

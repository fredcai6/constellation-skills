# Reviewer Handoff

## Gate
g7-implement (execute.json, work-id w3-promote) — reviewing the implementer's completed slice

## Survey State Location
Create your review survey checklist at `.agent-work/w3-promote/g7-review/review.json`.

## What Was Implemented
1 of 5 candidate `check: null` conditions across two files promoted, using only the engine's
existing `command` check kind (`decision:no-new-check-kinds`):

- `skills/scout/templates/SCOUT.template.json`'s `report.c1` ("SCOUT_REPORT written; candidates
  routed") — SPLIT promotion, existence+nonempty half only, against the fixed-path locator
  `.agent-work/SCOUT_REPORT.md`. Statement text left byte-identical, no `basis` field added.
  Shipped **REPORT-ONLY** (command always exits 0) because this file measured ZERO live check
  kinds anywhere before this gate — first use of any kind in this template defaults to
  report-only per `decision:blocking-where-adjudicated`, reversing every prior gate's own
  blocking-by-default (g1/g3/g4/g5 all cited a pre-existing live check in the same file to justify
  blocking; this file had none to cite). The named promotion trigger ("N clean report-only runs
  through this gate with zero false-refusals, reviewed at the next Cartographer/Scout-owning wave")
  is recorded in a new `map_check_note` field on the `report` task — a documented,
  template-only/read-by-no-code field (`docs/CHECKLIST_SCHEMA.md` line ~196), already used this
  exact way by `COMMANDER_SPINE.template.json`'s `context`/`plan` steps.
- `skills/cartographer/templates/CARTOGRAPHER.template.json` — **0 of 4 promoted, file untouched.**
  `context.c1`/`map-compliance.c1` pure judgment. `packets.c1`/`index-overlays.c1` declined: a
  git-diff-based "something under `docs/architecture/` changed" proxy verifies motion not
  correctness (locator-ambiguous), and independently this run's own `MISSION_FRAME.md` records the
  map as DEGRADED-UNPARSEABLE (`docs/architecture/` empty) — the handoff's own CRITICAL section
  bars a promoted check from depending on map state the repo cannot currently produce.

Promoting `report.c1` (the `report` task's only postcondition) cleared 1 all-null gate;
`falsifiable-all-null` corpus count dropped 14→13 (post-g5 baseline was 14).
`tests/test_validate_spine.py`'s floor was updated in the same edit (message text + numeric
threshold). Two new red-proof test classes added to `tests/test_checklist_engine.py`:
`ScoutW3PromotePromotions` (6 tests, including two report-only-specific tests: one proving
`advance` never blocks under any fixture, one proving the underlying shell probe still
discriminates via stdout) and `CartographerW3PromoteDeclined` (pins the zero-promotion decision
against future drift).

## How to Inspect the Diff
Uncommitted working tree (sitting on top of the already-committed g1/g3/g4/g5 promotions at HEAD
`d73c6b9a` — do not re-review those). `git status --porcelain` then `git diff` for the files named
below only.

## Task Statement
Promote the bucket-2 conditions in BOTH `skills/cartographer/templates/CARTOGRAPHER.template.json`
and `skills/scout/templates/SCOUT.template.json` per `notes-1.md`'s sections for each, using only
existing engine check kinds, with the report-only-by-default reversal explained above, red-proof
each promotion with an adversary-chosen mutation, keep the suite green at this gate boundary. Full
handoff: `.agent-work/w3-promote/crew-handoffs/g7-implementer-handoff.md`. Full result:
`.agent-work/w3-promote/crew-handoffs/g7-implementer-result.md`.

## Close Criteria
- `git diff --stat -- skills/cartographer/templates/CARTOGRAPHER.template.json` is empty — confirm
  the file and its overlay are genuinely untouched (byte-identical to HEAD).
- Exactly 1 condition changed in `SCOUT.template.json` (`report.c1`'s `check` field) plus the new
  `map_check_note` field on the `report` task; `context.c1`, `audit.c1`, `audit.p1`, and every
  other condition in the file untouched — verify against `git diff`.
- `report.c1`'s promoted shape: `command` kind, the shell command tests `-s` (nonempty, not merely
  `-f`/existence) against `<repo-root>/.agent-work/SCOUT_REPORT.md`, and unconditionally `exit 0`
  regardless of which branch fires. Confirm the command genuinely computes and prints a real
  verdict on both branches (it is not a no-op disguised as report-only) — run it yourself against
  both an empty/missing and a populated `SCOUT_REPORT.md` in a scratch directory.
- Independently verify the "zero live check kinds before this gate" claim for BOTH files:
  `git show HEAD:skills/scout/templates/SCOUT.template.json` and
  `git show HEAD:skills/cartographer/templates/CARTOGRAPHER.template.json`, dump every condition's
  `check` field, confirm all were `null` pre-edit. This is the load-bearing fact behind shipping
  report-only instead of blocking — verify it yourself rather than trusting the implementer's prose.
- `map_check_note`'s legitimacy as a field: independently confirm it is documented in
  `docs/CHECKLIST_SCHEMA.md` as template-only/read-by-no-code (grep the doc yourself), and that it
  does not collide with `decision:no-basis-backfill` (that ruling is specifically about the
  `basis` field, not this one) — confirm no `basis` field was added anywhere
  (`grep -n "basis" skills/scout/templates/SCOUT.template.json` should show nothing new).
- CARTOGRAPHER's decline: independently verify the DEGRADED-UNPARSEABLE map claim
  (`ls docs/architecture/` or equivalent) and that a git-diff-based packets/overlays proxy would
  genuinely be locator-ambiguous (would it falsely pass a stale map if something unrelated under
  `docs/architecture/` changed in the same commit?) — this is a judgment call the implementer made;
  re-derive it yourself rather than accepting the prose.
- Overlay (`.agent-work/templates/SCOUT.template.json`) byte-matches; confirm with
  `python3 scripts/check_template_overlay_freshness.py` (all 56 clean). Confirm
  `.agent-work/templates/CARTOGRAPHER.template.json` was correctly left untouched (0 edits means 0
  overlay sync needed).
- The red-proof test classes: does `ScoutW3PromotePromotions` (a) assert the exact shipped shape,
  (b) assert no other condition in the file changed, (c) attack with a genuinely adversarial
  mutation (an EMPTY file, not merely a missing one — attacks the `-s` boundary specifically), (d)
  prove `advance` never blocks regardless of fixture state, (e) prove the underlying probe's stdout
  still discriminates real state via the engine's own `_run_check_command`? Does
  `CartographerW3PromoteDeclined` genuinely pin something (not a vacuous test)?
- `tests/test_validate_spine.py`'s floor: independently re-run the corpus-wide
  `falsifiable-all-null` sweep pre/post-edit (`git stash` the two touched files, sweep, pop, sweep
  again) and confirm the 14→13 drop is real and correctly attributed to `report` clearing (it had
  exactly one postcondition, no preconditions).
- `docs/CHECK_SCRIPT_CENSUS.md`'s unwired-script list (`check_role_spine_bookends.py`,
  `check_skill_freshness.py`) — confirm neither was actually wired in this gate (the implementer
  claims neither fit); if that's wrong, flag it since g8 depends on this being accurate.
- Full suite green AFTER all of the above:
  `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q`.

## Allowed Scope
`skills/scout/templates/SCOUT.template.json`, `.agent-work/templates/SCOUT.template.json`,
`tests/test_checklist_engine.py` (new classes only), `tests/test_validate_spine.py` (floor
numbers/message only). You are reviewing, not editing — BLOCK with specific findings if something
is wrong, do not fix it yourself. `skills/cartographer/templates/CARTOGRAPHER.template.json` is
read-only for you too (verify it is untouched, do not edit it).

## Specific Exclusions
Do not touch or re-review `COMMANDER_SPINE.template.json`, `ADMIRAL_SPINE.template.json`,
`EXPLORER_SPINE.template.json`, or `CHARTER.template.json` (already integrated/committed). Do not
touch `checklist_engine.py` or `docs/CHECK_SCRIPT_CENSUS.md` (g8's job).

## Constraints the Implementation Must Respect
- `decision:no-new-check-kinds` — only `command` used, verify no new kind invented.
- `decision:no-basis-backfill` — verify NO `basis` field survives anywhere in the diff.
- `decision:blocking-where-adjudicated` — report-only default correctly applied given zero
  pre-existing live checks in either file; verify no promotion shipped blocking without a stated
  override reason (none should have).
- Compact-format JSON hand-edit discipline — the SCOUT diff should be a small, surgical change, not
  reflowed.

## Map Anchors (inbound)
- **Structural:** `skills/cartographer/templates/CARTOGRAPHER.template.json`,
  `skills/scout/templates/SCOUT.template.json`.
- **Decision anchors:** `decision:no-new-check-kinds` `@grade: settled/human`;
  `decision:no-basis-backfill` `@grade: settled/human`;
  `decision:blocking-where-adjudicated` `@grade: settled/human`.

## Evidence Produced
See `g7-implementer-result.md`'s Evidence section. Independently reproduce every command rather
than trusting the pasted output.

## Suggested Model Tier
simple bounded — mechanical verification against a well-specified handoff, small diff, but the
report-only-shape verification (does the command genuinely discriminate while never blocking)
needs actual execution, not just reading.

## Stop Conditions
Return BLOCK if: the promoted check's shape diverges from spec without a stated, sound reason; the
check does not genuinely `exit 0` unconditionally (a real blocking risk hiding inside a
"report-only" label); a `basis` field survives anywhere; `map_check_note` turns out not to be a
real documented field; the red-proof is not genuinely adversarial; the overlay is stale; the full
suite is not green; any excluded file was touched; CARTOGRAPHER's zero-promotion reasoning does not
hold up under your own independent verification of the DEGRADED-UNPARSEABLE map claim.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback. Write to
`.agent-work/w3-promote/crew-handoffs/g7-reviewer-result.md` before ending your turn.

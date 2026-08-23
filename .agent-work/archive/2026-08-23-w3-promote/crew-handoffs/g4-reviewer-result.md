# Review Result

## Assigned Gate
g4-review (work-id w3-promote) — independent review of g4-implement's completed slice
(`skills/explorer/templates/EXPLORER_SPINE.template.json` promotions)

## Result
**APPROVE**

## Handoff compliance
All Close Criteria independently reproduced and satisfied:

- Exactly 3 conditions changed — `init.c2`, `context.c1`, `spec.c1` — confirmed via
  `git diff --stat` (6 insertions/6 deletions = 3 single-line replacements in the shipped file,
  identical in the overlay) and via `git show HEAD:...` diffed against every task's postconditions.
  `route.c1` (line 81) and every other condition in the file is untouched.
- `init.c2`'s `command` string is byte-identical to `COMMANDER_SPINE.template.json`'s `init.c1`
  (g1) and `ADMIRAL_SPINE.template.json`'s `init.c2` (g3) — diffed all three directly, same seam
  exactly.
- `context.c1`/`spec.c1`: existence-only `command` checks (`test -s "<path>"`), `statement` text
  byte-unchanged (compared word-for-word against the pre-edit `git show HEAD:...` version), **no
  `basis` field** — `grep -n "basis" skills/explorer/templates/EXPLORER_SPINE.template.json`
  returns zero matches.
- `command`-kind eligibility independently confirmed against THIS template's own pre-existing
  checks: `init.c1`, `explore.c2`, `review.c1`, `confirm.c2`, `confirm.c3` are all `command`-kind
  at HEAD (measured directly, not trusted); `explore.c1`, `confirm.c1`, `route.c2` are the file's
  only `artifact`/`user-decision` uses. Not a first-use-in-file promotion for any of the 3, so
  `decision:blocking-where-adjudicated` permits blocking without a Commander consult — this
  correctly cites PLAN_CRITIC.md finding 3 (own-template's-live-kind-set, not corpus-wide), which
  I located and read in full.
- `route.c1`'s left-null disposition independently re-verified: the shared `scripts/` dir has no
  `verify_*.py --phase route` (grepped the actual `--phase` argument list in
  `verify_spec_confirmed.py`: only `review`/`confirm`); `skills/explorer/` has no `scripts/` dir of
  its own; and route's own imperative text shows all 3 named outcomes (hand off SHAPED_BRIEF.json /
  file a "shaped design" issue / shelve with the UNCONFIRMED header) are external actions (GitHub
  issue or handoff to another skill) with no differentiating local artifact — `SHAPED_BRIEF.json`
  is created upstream at `confirm`, identically regardless of which of the 3 outcomes `route` takes.
  The stated fallback holds.
- Overlay byte-matches (`diff` empty) and `check_template_overlay_freshness.py` reports all 56
  overlays clean.
- Red-proof test class `ExplorerSpineW3PromotePromotions`: read every method. Each of the 3
  discrimination tests uses a genuinely adversarial DEFECTIVE mutation, not a restatement of the
  check text — `init.c2` attacks a lease-status value (`"stale-explorer-lease"`) that the real
  `claim()`/`release()` machinery never legitimately writes (not merely "key missing"); `context.c1`
  and `spec.c1` attack the EXISTING-but-EMPTY boundary the `-s` flag adds over plain existence, not
  the easier "file missing entirely" case a different assertion already covers.
- `tests/test_validate_spine.py`'s floor: independently re-ran the corpus-wide
  `falsifiable-all-null` sweep both at the current worktree state (**15**) and, via `git stash`, at
  the pre-edit HEAD (**17**) — the 17→15 drop is real and correctly attributed to
  `context.c1`/`spec.c1` clearing their single-postcondition all-null gates (no other template
  contributes any all-null fault before or after this edit). The numeric floor (`>= 15`) was
  already `15` before this edit (set as a floor below the then-measured 17); only the message text
  changed, matching the implementer's claim.
- Full suite green: `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q`
  → `643 passed, 19 skipped, 150 subtests passed` — matches the result doc exactly, independently
  reproduced.

## Scope drift
None. `COMMANDER_SPINE.template.json`, `ADMIRAL_SPINE.template.json`, and `checklist_engine.py` do
not appear anywhere in `git diff --name-only` — specific exclusions honored.
`tests/test_checklist_engine.py`'s diff is a pure 288-line append at end-of-file, entirely inside
the new class; no pre-existing test was touched. `tests/test_validate_spine.py`'s diff touches only
the floor assertion's message string. `g4-implementer-handoff.md`, `execute.json`, and `notes-1.md`
also show modified in `git status`, but these are the Commander's own pre-dispatch handoff
amendment and spine/notes bookkeeping (not implementer-authored content), out of this gate's
allowed-scope concern.

## Evidence verdict
All required evidence independently reproduced and matches the result doc's pasted output exactly
(JSON parse OK; overlay freshness 56/56 clean; targeted suite 643 passed/19 skipped/150 subtests;
isolated `-k ExplorerSpineW3Promote` run; `git check-ignore` exit=1 on both deliverable paths). Test
mode was test-after per the handoff; satisfied.

## Code/doc quality
Compact-format JSON hand-edit discipline honored — diff is exactly 3 single-line replacements per
file (`git diff --stat`: 6 insertions/6 deletions), no reflow. The new test class is well-documented
(class docstring explains the split-promotion reasoning, the `route.c1` decline, and the
`no-basis-backfill` compliance; each adversarial mutation is commented with WHY it is adversarial
rather than a restatement).

## Independently re-verified: the Commander's `basis`-field correction

This was the handoff's highest-priority ask, so I traced it fully rather than trusting either the
implementer's or the Commander's framing.

**No trace of `basis` survives.** `grep -n "basis"` across the shipped
`EXPLORER_SPINE.template.json` returns zero hits. In `tests/test_checklist_engine.py`, every
`basis` mention inside the new `ExplorerSpineW3PromotePromotions` class (docstring prose at lines
~9273–9285, and `test_context_c1_and_spec_c1_keep_their_unsplit_statement_and_no_basis` at line
9386) documents the field's *absence* — `assertNotIn("basis", context_c1)` and
`assertNotIn("basis", spec_c1)` are the only assertions touching it. All other `basis` references
in the test file (e.g. `_basis_gate`, `test_populated_file_basis_renders_basis_line`, the
`plan.c2/c4/c5` pins at line 8544+) are pre-existing w2-basis infrastructure, confirmed untouched
by this gate's diff (the entire diff to this file is an append at EOF).

**The underlying premise independently holds — this is not a narrow "bulk backfill on untouched
conditions" rule.** I could not locate `LAUNCH_ORDER-w3-promote.md` anywhere in the repo (searched
by exact filename and by the string "Pre-Rulings" — no match; see Out-of-scope observations). The
actual authoritative text lives in `MISSION_FRAME.md`'s Governing Constraints
(`decision:no-basis-backfill` — "`basis` field is `w3-basis`'s population; do not roll it out
here") and its Out of Scope section, which lists **two separate exclusions**: "The `basis` field
**and** any `basis` backfill (`w3-basis`'s population, `decision:no-basis-backfill`)." That "and"
is doing real work: the ruling bars the `basis` field itself, categorically, for this wave's own
work — not merely rolling it out onto conditions this wave leaves otherwise untouched. A newly
promoted condition is squarely inside "this wave's own work." So the implementer's first pass (an
otherwise well-reasoned move, citing real `COMMANDER_SPINE` precedent) was a genuine violation of
this run's own governing constraint, not a defensible edge case, and the Commander's strip-and-fix
is correct on independent re-derivation, not merely trusted.

## Reconciliation check
No architecture-significant structural change — this reuses the engine's existing `command`
check-kind machinery, read-only; `checklist_engine.py` is untouched. `map/INDEX.md` is untouched by
this gate's diff.

## Blockers
- none

## Out-of-scope observations
- `route.c1` remains a genuine future null-check candidate should routing tooling ever record a
  per-outcome artifact (a `--phase route` verifier or a persisted routing-disposition file) — the
  implementer already surfaced this; independently confirmed real, no action needed now.
- The handoff cites `LAUNCH_ORDER-w3-promote.md`'s "Pre-Rulings section" for
  `decision:no-basis-backfill`'s text, but no file of that name exists anywhere in this repo
  (checked by exact filename and by grepping for a "Pre-Rulings" header). The actual text lives in
  `MISSION_FRAME.md` instead. Not a blocker — I located the real source and the pre-ruling itself is
  genuine and was independently re-verified above — but worth fixing at whatever upstream template
  stamps that citation string into Commander-authored reviewer handoffs, so a future reviewer does
  not spend time chasing a dead file reference.

## Workflow Feedback

- **Handoff gaps:** the one concrete gap was the `LAUNCH_ORDER-w3-promote.md` citation (see
  Out-of-scope observations) — the file it points to does not exist in this repo; `MISSION_FRAME.md`
  serves the same role here and carries the actual pre-ruling text.
- **Context rediscovered:** had to independently work out that `MISSION_FRAME.md`'s Out of Scope
  section states the `basis`-field exclusion as two separate clauses ("the field itself" and "any
  backfill") — the handoff's own framing of the question ("is it only about bulk backfill across
  untouched conditions?") could have pointed straight at that section instead of a non-existent
  launch-order file, which would have saved the file-hunt.
- **Instructions improvised around:** none — the handoff's explicit list of what to re-derive
  independently (basis absence, `command`-kind eligibility, `route.c1`'s null disposition, the
  17→15 floor) mapped cleanly onto reproducible commands.
- **What would have made this easier:** correcting the `LAUNCH_ORDER-w3-promote.md` citation to
  `MISSION_FRAME.md` (or wherever this run's actual pre-rulings live) in whatever template stamps
  reviewer handoffs for this epic.

## Return status
complete

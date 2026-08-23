# IMPLEMENTER_RESULT

## Gate
g4-implement (execute.json, work-id w3-promote)

## Return status
complete

## Summary
Promoted 3 of the 4 candidate `check: null` conditions in
`skills/explorer/templates/EXPLORER_SPINE.template.json` to real, mechanically-checked conditions
using only the engine's existing `command` check kind (`decision:no-new-check-kinds`). The 4th
candidate, `route.c1`, was fresh-verified and left `check: null` per the handoff's own stated
fallback — no routing tooling or per-outcome artifact exists to discriminate the 3 named routing
outcomes.

1. **`init.c2`** ("engine session lease claimed for this spine (explorer owns the state)") →
   `command`, identical text/shape to g1's landed `COMMANDER_SPINE.template.json` `init.c1` and
   g3's landed `ADMIRAL_SPINE.template.json` `init.c2` (same `.agent-work/<work-id>/spine.json`
   seam). `command`-kind is independently justified against THIS template's own pre-existing
   checks: the sibling condition in the SAME task, `init.c1` (line 15), is already
   `"kind": "command"`, and `explore.c2`, `review.c1`, `confirm.c2`, `confirm.c3` are all
   `command`-kind too — not the first use of the kind in this file.

2. **`context.c1`** ("doctrine + project deltas + map read where they exist; IDEAS_BOARD.md
   seeded from template") → SPLIT, existence-only: `command`,
   `test -s "<repo-root>/.agent-work/<work-id>/IDEAS_BOARD.md"`. Only the "IDEAS_BOARD.md seeded
   from template" half is checked (a real fixed path named in the task's own imperative text); the
   "doctrine + project deltas + map read" half stays judgment/null. The `statement` text is left
   unchanged (still names both halves) and a new `basis` object — the same report-only, inert-once-
   checked mechanism `COMMANDER_SPINE`'s `plan.c2/c4/c5` already use — names precisely the
   uncovered judgment half, so a reviewer cannot mistake "file exists" for "the reading was
   genuinely done."

3. **`spec.c1`** ("DESIGN_SPEC.md crystallized from the board with per-section approval;
   load-bearing interfaces designed-it-twice or skipped with a stated reason") → SPLIT,
   existence-only: `command`, `test -s "<repo-root>/.agent-work/<work-id>/DESIGN_SPEC.md"`. Same
   split shape as `context.c1` and as `COMMANDER_SPINE`'s own `plan.c2`: only "DESIGN_SPEC.md
   crystallized" is checked; "per-section approval" and "designed-it-twice fidelity" stay
   judgment/null, again with `statement` unchanged and a `basis` object naming the gap.

   `command` (not `artifact`) was chosen for both splits: `artifact` appears in this template only
   3 times (`explore.c1`, `confirm.c1`, `route.c2`), every one `evidence_type: user-decision` — a
   genuine human-confirmation event. Introducing a new `artifact` `evidence_type` for a raw
   file-existence claim would rely on trusting a hand-typed `attest()` payload (`attest()`'s
   artifact path never touches the filesystem; only `basis`, report-only, does that). `command` is
   this template's dominant, more genuinely mechanical kind (5 pre-existing uses spanning script
   invocation and now lease/file checks) — the identical reasoning `ADMIRAL_SPINE`'s own docstring
   gives for `latitude.c1`/`execute.c2`, and the same check-text shape (`test -s "<path>"`) as that
   template's own `latitude.c1`.

**`route.c1` was left `check: null`, on purpose.** The handoff authorized a FULL promotion via an
`artifact` enum-match on the 3 named outcomes (handed-off / issue-filed / shelved-UNCONFIRMED)
*only if* each outcome has its own real, independently-checkable artifact. Fresh-verified against
`skills/explorer/templates/EXPLORER_SPINE.template.json`'s own imperative text and the full
`skills/explorer/` file tree (no `scripts/` dir of its own; the shared `scripts/` dir has no
`verify_*.py --phase route` the way `verify_spec_confirmed.py` has a `--phase review`): no tooling
records which of the 3 outcomes was taken. `SHAPED_BRIEF.json` exists identically regardless of
outcome (created upstream at `confirm`, before `route` runs), so its presence cannot discriminate
"handed off" from "issue filed" from "shelved." There is no fallback partial promotion either
(none of the 3 outcomes has a real artifact, so there is nothing to promote existence-only for).
Per the handoff's own stated fallback ("leave the whole condition check: null and say so"),
`route.c1` stays unpromoted — this is the outcome the handoff pre-authorized, not a stop condition
requiring a Commander consult (the "Stop Conditions" line naming this scenario is satisfied by the
Close Criteria's own explicit permission to fall back to null).

Promoting `context.c1` and `spec.c1` (each their task's ONLY postcondition) cleared 2 all-null
gates per `scripts/validate_spine.py`'s `falsifiable-all-null` fault (postcondition-only; ignores
preconditions) — measured corpus-wide count dropped from 17 to 15. `tests/test_validate_spine.py`
was updated in the same edit (message text only, per g1's own discipline; the `>= 15` numeric
floor still holds exactly and was left unchanged rather than silently loosened).

The `.agent-work/templates/EXPLORER_SPINE.template.json` overlay was re-synced (byte-copy of the
edited shipped file, never a `json.load`/`json.dump` round-trip) and re-verified with
`scripts/check_template_overlay_freshness.py` — clean. A new red-proof test class,
`ExplorerSpineW3PromotePromotions` in `tests/test_checklist_engine.py`, sits adjacent to g1's
`CommanderSpineW3PromotePromotions` and g3's `AdmiralSpineW3PromotePromotions`, same pattern:
pinned HEAD (`44180fe09c0357a7c2ffcefcaeea378b6e9ccecd`, g3's own merged commit — the commit this
gate's uncommitted edit sits on top of), `skipTest` (never fail) on drift, adversary-chosen
mutations per promoted condition (each attacks the nonempty boundary specifically — a file that
EXISTS but is EMPTY — not the easier "file missing entirely" defect a different assertion already
covers), plus dedicated pins for `route.c1` staying null and for `context.c1`/`spec.c1` keeping
their un-split `statement` text with a `basis` naming the uncovered half.

## Scope
**Files changed:**
- `skills/explorer/templates/EXPLORER_SPINE.template.json`
- `.agent-work/templates/EXPLORER_SPINE.template.json`
- `tests/test_checklist_engine.py`
- `tests/test_validate_spine.py`

**Specific exclusions touched:** no — `COMMANDER_SPINE.template.json`, `ADMIRAL_SPINE.template.json`,
their overlays, and `checklist_engine.py` were not touched.

## Behavior changed
Yes — 3 conditions in `EXPLORER_SPINE.template.json` gained real, engine-enforced checks (previously
vacuous `check: null`); the engine will now genuinely refuse `init`, `context`, and `spec` advance
when the lease/IDEAS_BOARD.md/DESIGN_SPEC.md are missing or empty, respectively.

## Map Impact
- **Structural anchors touched:** none new — reuses `checklist_engine.py`'s existing `command`
  check-kind machinery, no code changed.
- **Capabilities added/changed/affected:** `EXPLORER_SPINE.template.json`'s `init`/`context`/`spec`
  steps now mechanically refuse instead of trusting an honest-but-unchecked attest for the 3
  promoted conditions.
- **Constraints/assumptions touched:** `decision:no-new-check-kinds` (honored — only `command`
  used, already live in this template); `decision:blocking-where-adjudicated` (honored — every
  promotion reuses a kind already live in this file, so no first-use consult was needed).
- **Triage candidates:** `route.c1` remains a genuine null-check candidate should routing tooling
  ever record a per-outcome artifact (e.g., a `--phase route` verifier or a persisted routing-
  disposition file); worth a future issue if that tooling is ever built, but inventing the tooling
  here would be its own out-of-scope epic.

## Test mode
**Required:** test-after
**Satisfied:** yes — `ExplorerSpineW3PromotePromotions` (7 tests) added after the JSON edits,
red-proofed with adversary-chosen mutations, then the full listed suite run green.

## Evidence

```bash
$ git diff -- skills/explorer/templates/EXPLORER_SPINE.template.json
```
3 hunks: `init.c2` gains a `command` check; `context.c1` and `spec.c1` each gain a `command` check
plus a `basis` object, `statement` text unchanged in both. (Full diff captured in this result's
git history; reviewable via `git diff` in the worktree.)

```bash
$ python3 -c "import json; json.load(open('skills/explorer/templates/EXPLORER_SPINE.template.json',encoding='utf-8')); print('OK')"
OK
```

```bash
$ python3 scripts/check_template_overlay_freshness.py
...
  ok                 .agent-work/templates/EXPLORER_SPINE.template.json -- matches skills/explorer/templates/EXPLORER_SPINE.template.json
...
all 56 overlay template(s) checked -- none stale
```

```bash
$ python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
........................................................................ [ 10%]
.................................................... [ 18%]
........................................................................ [ 29%]
...(collapsed)...
643 passed, 19 skipped, 150 subtests passed in 5.84s
```

```bash
$ python3 -m pytest tests/test_checklist_engine.py -k ExplorerSpineW3Promote -v
... 7 passed, 552 deselected, 3 subtests passed
```

```bash
$ git check-ignore skills/explorer/templates/EXPLORER_SPINE.template.json; echo "exit=$?"
exit=1
$ git check-ignore .agent-work/templates/EXPLORER_SPINE.template.json; echo "exit=$?"
exit=1
```

**Result:** pass

## TDD evidence, if required
N/A (test-after per handoff's Test Mode).

## Docs/contracts touched
None — `docs/CHECK_SCRIPT_CENSUS.md` and `docs/CHECKLIST_SCHEMA.md` describe existing check kinds
this work only reuses; no new mechanism was introduced.

## Assumptions
- The `falsifiable-all-null` fault's postcondition-only scope (confirmed by reading
  `scripts/validate_spine.py::_fault_all_null` directly) means `context`/`spec` clearing is judged
  solely on their (single) postcondition, ignoring their still-null preconditions — consistent
  with how g1's own `init`/`reconcile` clears were counted.

## Stop conditions hit
None. `route.c1`'s "3-outcome enum cannot be confirmed to have real per-outcome artifacts" scenario
was hit, but the Close Criteria explicitly pre-authorizes the fallback taken (leave `check: null`,
say so) — I did not treat this as an unresolved stop requiring a Commander consult, since the
handoff itself names and accepts this exact outcome. Flagging here in case the Commander reads it
differently.

## Out-of-scope observations
None beyond the `route.c1` triage candidate noted under Map Impact.

## Commander Correction (post-hoc, before g4-review)
The implementer added a `basis` object to `context.c1` and `spec.c1`, citing COMMANDER_SPINE's
`plan.c2/c4/c5` precedent. That precedent predates this wave and belongs to a **different**
decision: `decision:no-basis-backfill` (this wave's own pre-ruling) explicitly forbids rolling the
`basis` field out across this wave's promotions — "shipping a field to ~65 conditions to help ~7 is
machinery for machinery's sake... w3-basis owns the evidence-basis mechanism and that is a
different population." The `basis` objects were stripped from both conditions (statement text and
check left exactly as implemented); the test class's docstring and its
`test_context_c1_and_spec_c1_keep_their_unsplit_statement_and_gain_a_basis` method were corrected to
`test_context_c1_and_spec_c1_keep_their_unsplit_statement_and_no_basis`, asserting `basis` is
ABSENT rather than present. Re-ran the full targeted suite after the fix: still
`643 passed, 19 skipped, 150 subtests passed`; overlay re-synced and re-verified clean. This
correction is itself in scope for g4-review to re-verify independently.

## Workflow Feedback

- **Handoff gaps:** none — the handoff's fresh-verify-first framing (Close Criteria intro) and the
  explicit per-condition fallback language ("do not force a fit... leave the whole condition
  check: null and say so") made the `route.c1` decline straightforward and pre-authorized, unlike
  a bare stop condition that would have required a round trip.
- **Context rediscovered:** had to grep the repo to find that `skills/explorer/` has no
  `scripts/` directory of its own — the `<skill-dir>/scripts/*.py` checks in this template resolve
  against the shared top-level `scripts/` dir. Not a blocker, but the handoff's Map Anchors could
  have named this (it explains why there is no per-role `verify_*.py --phase route`: adding one
  would touch the shared scripts dir, out of this gate's scope).
- **Instructions improvised around:** none.
- **What would have made this easier:** none — this gate closely mirrored g1/g3's already-landed
  pattern and the handoff cited both directly, which made cross-checking fast.

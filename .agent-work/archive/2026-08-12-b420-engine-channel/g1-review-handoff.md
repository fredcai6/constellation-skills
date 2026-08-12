# Reviewer Handoff

## Gate
g1-review

## What was implemented
Fix for issue #420 (epic #418, workstream B) in `scripts/checklist_engine.py`:
1. RAIL echo de-dup, `current` verb only (verb-aware — the other 5 railed verbs keep the full
   imperative unchanged).
2. `anchors`/`constraints` rendering added to `state()`/`render_human()`.
3. A completeness property test enumerating Task fields.

**One rework cycle already happened, before you were dispatched.** The implementer's first pass on
(2) broke on a real corpus shape it hadn't tested: `anchors: {category: "<plain string>"}` — the
exact shape `g1-review`'s OWN anchors carry in the shipped `EXECUTE_PLAN.template.json` (line 41).
It rendered as one line PER CHARACTER (~90 lines) instead of the field. The Commander caught this
independently, sent it back with a live reproduction, and the implementer fixed it with a new
`_anchor_category_items()` helper plus a regression test sourced verbatim from that shipped
template line — already re-verified once by the Commander. Your job is to verify it holds under
your own independent reproduction, not to re-discover it from scratch.

Full detail: `.agent-work/b420-engine-channel/g1-implement-result.md` (IMPLEMENTER_RESULT, updated
in place with the rework's own red/green evidence) — read it in full, then verify its claims
independently rather than trusting them.

## How to inspect the diff
```bash
cd C:/Programs/constellation-skills-wt/epic418-b-420
git diff scripts/checklist_engine.py tests/test_checklist_engine.py
git diff --stat
```
Confirm only these two files changed (`git status --porcelain`), and that `_check_condition` is
untouched (`git diff scripts/checklist_engine.py | grep _check_condition` — expect no hits).

## Task statement
Verify the fix actually satisfies issue #420's three deliverables, the launch order's ordering
constraint (workstream C is blocked on this landing), and the shared-file fence with D (#422) —
without re-deriving whether the underlying defects are real (they are; verified live by the
Commander before this gate opened).

## Close criteria
- `python -m pytest tests/test_checklist_engine.py tests/test_spine_rail.py -q` green, and the
  reported count is 388 (baseline) + N new tests with zero regressions — reproduce this yourself,
  do not trust the pasted number.
- On the `current` verb, a mid-flight fixture's imperative appears exactly once in the CLI-wrapped
  output (through `dispatch()`, not the bare `current()` function).
- On every OTHER railed verb (claim/start/advance/attest/attach), the SAME mid-flight fixture still
  shows the FULL imperative, unchanged — verify at least one directly, e.g. `E._rail("start", cl)`.
- `_RAIL_STRINGS` dict values are byte-identical to `git show HEAD:scripts/checklist_engine.py` (i.e.
  pre-change) — diff them explicitly, don't eyeball it.
- **Load-bearing, test this yourself, not just via the implementer's own tests:** render a gate whose
  `anchors` field is `{"<category>": "<plain string>"}` (the shape used by `g1-review`'s OWN anchors
  in `skills/commander/templates/EXECUTE_PLAN.template.json` line 41, and in this run's own
  `execute.json`) through `current()` and confirm it prints as ONE readable line, not one line per
  character. This exact shape broke on the implementer's first pass (Commander caught it and sent it
  back for rework) — confirm the fix actually generalizes rather than special-casing the one example
  given in the rework request.
- `anchors`/`constraints` absent or empty on a gate → `current`'s output is byte-identical to
  pre-change (spot-check against an existing golden).
- The new `TaskFieldCompleteness` test is a real enumeration (loops over the fixture's own populated
  fields minus a documented, justified exclusion list) — not a hardcoded check of only
  `anchors`/`constraints` by name. Read the exclusion list; each entry should carry a stated reason,
  not just be left out silently.

## Allowed scope (yours: verification only)
Read `scripts/checklist_engine.py`, `tests/test_checklist_engine.py`, `tests/test_spine_rail.py`,
`docs/CHECKLIST_ENGINE_DESIGN.md`, `docs/CHECKLIST_SCHEMA.md`. Run tests and ad hoc Python snippets
to reproduce claims. Do not edit source; this is a review gate.

## Specific exclusions
Do not evaluate workstream C's relocation work, D's invariant-check path, the DIGEST-staleness
observation, or RAIL-echo compliance-neutrality — all explicitly out of this issue's scope per the
launch order; note if the diff touches any of them (it should not).

## Constraints
- Verify goldens genuinely preceded the fix — ask to see (or independently reproduce) a RED run
  against `git stash`'d source, if the implementer's pasted red-run evidence is not convincing on
  its own.
- Verify no touch to `_check_condition` or other invariant-check code (D's #422 fence).
- Verify the docstring citation fix (`render_human()`, previously cited a stale line 818) actually
  points somewhere correct now.

## Map Anchors (inbound)
Inherits g1-implement's anchors — same structural/capability/constraint/decision/evidence anchors;
review verifies the change against them.

## Deliverable Path Check
N/A — review produces no new committed file, only a REVIEW_RESULT artifact attached to the engine.

## Required Evidence
- Your own independently-reproduced test run output (not copy-pasted from the implementer's result).
- Your own independently-reproduced anchors-dict-of-string rendering check (the load-bearing item
  above) — paste the actual output.
- APPROVE or BLOCK verdict with findings.

## Verification Commands
```bash
python -m pytest tests/test_checklist_engine.py tests/test_spine_rail.py -q
git diff --stat
git diff scripts/checklist_engine.py | grep -c _check_condition
```

## Suggested Model Tier
Sonnet.

## Authority
Verdict is yours (APPROVE/BLOCK with findings); scope/decision questions route back to the
Commander, not to you to resolve unilaterally.

## Stop Conditions
Stop and return if: you cannot reproduce a claimed evidence item, you find a defect the implementer
didn't disclose, or you need a decision outside your authority.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE/BLOCK), findings, evidence reproduced, workflow feedback.
Deliver via SendMessage to your dispatcher before ending your turn.

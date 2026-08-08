# Reviewer Handoff — g2-review

## Gate
`g2-review` (execute.json, work-id `b433-render-directives`, issue #433)

Worktree, and the only place to work: `C:/Programs/constellation-skills-wt/r418-433`. Absolute paths.

## Survey State Location

Create your review survey checklist at
`C:/Programs/constellation-skills-wt/r418-433/.agent-work/b433-render-directives/g2-review/review.json`
— under the issue workbench, never at the worktree root.

## What Was Implemented

`tests/test_checklist_engine.py`'s `class TaskFieldCompleteness` was rewritten so it can actually
FAIL for the shapes the corpus carries. Before this change it could not: `directives` sat in
`_EXCLUDED_FIELDS`, and even un-excluded, `_flatten` returned `[]` for the nested-dict shape every
populated corpus block carries — so the loop body never ran, the property asserted nothing, and it
reported green.

Five changes: `directives` un-excluded; `_flatten` replaced by a total `_leaf_texts` recursive
extractor; the single `checked_any` flag replaced by a per-field ledger; a new test asserting the
fixture's key set is a superset of the engine's own `_build_amend_task` output; and an in-suite
negative self-test that drives the same assertion path against a render with `directives` stripped
and asserts it raises naming the field. Plus one carry-over: `_render_directive_lines`'s flat-list
branch was silently dropping non-string items and is now total.

## How to Inspect the Diff

The review target is the **UNCOMMITTED working tree**, not `git diff main...HEAD`.

```bash
cd C:/Programs/constellation-skills-wt/r418-433
git status --porcelain
git diff scripts/checklist_engine.py tests/test_checklist_engine.py
```

Note the diff spans **two gates**. `g1` (already reviewed and integrated) owns `state()`'s
passthrough, `_directive_leaf`, `_render_directive_lines`, `render_human()`'s emission site, and
`class RenderDirectives`. **You are reviewing g2**: `class TaskFieldCompleteness`, the new tests, and
the one-line list-branch carry-over inside `_render_directive_lines`. Do not re-litigate g1.

Changes under `.agent-work/` are engine state and crew artifacts, not deliverables.

## Task Statement

The implementer's full handoff, which is binding on this review:
`.agent-work/b433-render-directives/crew-handoffs/g2-implement-HANDOFF.md`
Its result:
`.agent-work/b433-render-directives/crew-handoffs/g2-implement-IMPLEMENTER_RESULT.md`

## Close Criteria — verify each, and say how you verified it

**The review's whole point is falsifiability.** A property observed only passing is a check that
cannot fail, and reporting it green is the failure mode this gate exists to catch. So:

1. **Independently REPRODUCE red-proof R2** — make the extractor return `[]` for dicts (the old
   `_flatten` behaviour) and confirm the suite goes RED with the ledger set-mismatch **naming the
   fields**, not green. Revert.
2. **Independently REPRODUCE red-proof R4** — add a populated fixture field whose value flattens to
   nothing, confirm it fails **by name**. Revert.
3. **Independently REPRODUCE red-proof R5** — add a field to `_build_amend_task` in
   `scripts/checklist_engine.py` and not to the fixture; confirm the superset assertion fails **by
   name**. Revert.
   Paste what you actually saw for each. Do not accept the implementer's captures.
4. **The ledger is per-field, not one flag.** Read it. A single boolean anywhere in that loop is a
   BLOCK — one flag lets any field cover for any other, which is the specific defect this replaces.
5. **The test's leaf extractor is NOT the renderer's.** No import, no shared helper. A shared bug
   would render nothing and assert nothing, in agreement, and both sides would report green.
6. **The class docstring states the residual limit** — that this closes the hole for fields the
   *engine* introduces, and a field introduced only by a template still needs a human to add it —
   rather than implying coverage the property lacks.
7. **Every remaining entry in `_EXCLUDED_FIELDS` still carries its stated reason**, and only
   `directives` was removed.
8. **The negative self-test drives the real assertion path**, not a hand-rolled copy of it. If it
   asserts against edited output text rather than a real render, say so.
9. **The flat-list carry-over is total** and has a test.
10. **Suite:** `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py` — run it
    yourself, capture the REAL exit code (`echo "EXIT=$?"`). Never `py` for pytest (#454). Confirm the
    working tree carries no residual break from your own reproductions when you finish.

## Allowed Scope (what the implementer was permitted to touch)

`tests/test_checklist_engine.py` — `class TaskFieldCompleteness` in full, plus one test for the
carry-over. `scripts/checklist_engine.py` — ONLY the list branch of `_render_directive_lines` and its
docstring.

## Specific Exclusions (a touch here is a BLOCK)

- `docs/CHECKLIST_SCHEMA.md` — gate `g3-schema` owns it.
- Any other engine change beyond the one-line list branch. In particular `_build_amend_task` and
  `append()` must be **unchanged** in the final tree.
- `scripts/collect_feedback.py` (#464), `episodes/` (#460),
  `scripts/verify_worktree_precondition_coverage.py` (#436).

## Constraints the Implementation Must Respect

- No new dependency.
- The ledger's failure message names the offending field. "the loop asserted nothing" is the message
  this change exists to replace.
- Match the test module's idiom and comment density.

## Map Anchors (inbound)

Inherited from `g2-implement`:

- **Structural:** `tests/test_checklist_engine.py` — `class TaskFieldCompleteness` (find by symbol,
  line numbers moved); `scripts/checklist_engine.py` — `_build_amend_task` ~2102, `append()` ~2314,
  `_render_directive_lines` ~1689.
- **Capability:** the Task field contract. The engine's own builder is the enumeration that can be
  checked mechanically — that substitution for the schema table is cold-critic finding 1.
- **Constraints/assumptions:** `constraint:a-check-that-cannot-fail` — a guard whose output is
  identical in the healthy and the defective world is not a guard.
- **Decision anchors:**
  - `decision:per-field-ledger-is-the-class-fix` `@grade: settled/measured · leans g2`
  - `decision:independent-extractor` `@grade: settled/human · leans g2`
- **Evidence expectations:**
  `claim:the-completeness-property-fails-when-a-populated-field-is-unrendered`.
- **Map confidence flags:** no `docs/architecture` map; orientation DEGRADED by standing condition.

## Evidence Produced (reproduce it, do not accept it)

- R2/R4/R5 captures under `.agent-work/b433-render-directives/evidence/g2-r{2,4,5}-*.txt`.
- Final suite: `349 passed, 30 subtests passed`, `EXIT=0` (baseline before g2 was 346).
- Wiring grep `_build_amend_task` in `tests/`: count 5, one live call site.
- The implementer reports a live residual: `anchors` is emitted by **neither** builder — it is in the
  fixture only because a human put it there. Confirm that is stated honestly in the docstring rather
  than glossed.

## Suggested Model Tier

**Stronger.** Three of the checks require you to break the tree, observe a specific red, and restore.

## Stop Conditions

Return BLOCK if: the diff cannot be accessed; any red-proof comes back GREEN or reds for the wrong
reason; the ledger is not per-field; the extractor is shared with the renderer's; an excluded file was
touched; or a policy decision is needed before a verdict.

## Return Format

Return REVIEW_RESULT with an explicit `verdict:` line reading exactly `APPROVE` or `BLOCK`, then
per-check findings (one per close criterion, each with how you verified it), blockers, out-of-scope
observations, and workflow feedback.

Write it to:
`C:/Programs/constellation-skills-wt/r418-433/.agent-work/b433-render-directives/crew-handoffs/g2-review-REVIEW_RESULT.md`

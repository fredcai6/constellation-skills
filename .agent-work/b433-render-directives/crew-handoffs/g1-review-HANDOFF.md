# Reviewer Handoff — g1-review

## Gate
`g1-review` (execute.json, work-id `b433-render-directives`, issue #433)

Worktree, and the only place to work: `C:/Programs/constellation-skills-wt/r418-433`. Absolute paths.

## Survey State Location

Create your review survey checklist at
`C:/Programs/constellation-skills-wt/r418-433/.agent-work/b433-render-directives/g1-review/review.json`
— under the issue workbench, never at the worktree root.

## What Was Implemented

A populated `directives` block now reaches the agent through the engine's `current` projection.
`state()` passes the field through beside `constraints`/`anchors`; `render_human()` emits a
`directives:` block between `anchors:` and `next:`, formatted by a new `_render_directive_lines()`
with a `_directive_leaf()` scalar speller. Both live corpus shapes are served: a dict of
name -> nested contract dict (all 8 populated corpus gates), and a flat list of strings (what the
schema declares and the `add` amend op accepts).

## How to Inspect the Diff

The review target is the **UNCOMMITTED working tree**, not `git diff main...HEAD`.

```bash
cd C:/Programs/constellation-skills-wt/r418-433
git status --porcelain
git diff scripts/checklist_engine.py tests/test_checklist_engine.py
```

Only those two files are in scope for you. Changes under `.agent-work/` are the engine's own state
writes and the crew's artifacts — not this gate's deliverable, and not defects.

## Task Statement

The implementer was told: make a populated `directives` block reach the agent through `current`;
author the golden over the ACTUAL shipped `skills/commander/templates/COMMANDER_SPINE.template.json`
`execute` gate BEFORE touching the renderer and capture it RED; add a dedicated formatter beside
`_render_anchor_lines()` handling both corpus shapes; keep the first `ACTIVE` line byte-identical;
keep absent/empty silent; keep `state()` pure.

Its full handoff:
`.agent-work/b433-render-directives/crew-handoffs/g1-implement-HANDOFF.md`
Its result:
`.agent-work/b433-render-directives/crew-handoffs/g1-implement-IMPLEMENTER_RESULT.md`

## Close Criteria — verify each, and say how you verified it

1. **The golden was captured RED before the change.** This is the criterion the gate exists for. A
   golden written after the fact certifies whatever the code now emits and proves nothing. The
   implementer's capture is at `.agent-work/b433-render-directives/evidence/g1-RED-capture.txt` and
   claims `git diff --quiet scripts/checklist_engine.py` passed in the same shell invocation.
   **Do not take that on report — reproduce it.** Stash or revert only the `checklist_engine.py`
   hunks, run the new `RenderDirectives` tests, confirm they fail, restore. Paste what you actually saw.
2. **The first line of `current` is byte-identical**: `ACTIVE {id} [{status}] — {imperative}`.
   `GoldenOutputBriefing` (~3779) and `ShippedTemplates` must be green and unmodified.
3. **An absent `directives` and an empty `directives` each add zero output** — same behaviour as
   `constraints`/`anchors`. Check the test exists AND that it would fail if the guard were removed.
4. **`state()` gained no side effect.** Pure passthrough, no check re-runs (INV-2). Read the added line.
5. **Both shapes render.** The nested-dict shape and the flat-list-of-strings shape, each with its own
   test. A dict-only renderer is a BLOCK: `tests/test_checklist_engine.py:~4038`'s
   `TaskFieldCompleteness` fixture carries the flat-list shape, and narrowing to dicts would silently
   reinstate the defect for it.
6. **The renderer is wired.** `_render_directive_lines` has at least one call site outside its own
   definition. A renderer nothing calls is shipped-inert — the exact defect class this issue closes.
7. **Test suite:** `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py` — run
   it yourself, capture the REAL exit code (`echo "EXIT=$?"`), do not read green off the summary line.
   Never use `py` for pytest (#454).

## Allowed Scope (what the implementer was permitted to touch)

`scripts/checklist_engine.py` — `state()`, the new formatter, the `render_human()` emission site and
docstrings there. `tests/test_checklist_engine.py` — new tests plus minimal reconciliation of any
existing test whose expected output legitimately changed.

## Specific Exclusions (a touch here is a BLOCK)

- `class TaskFieldCompleteness` in `tests/test_checklist_engine.py` — gate `g2-implement` owns it in
  this same run. In particular `_EXCLUDED_FIELDS` must still contain `directives`, and `_flatten` must
  be unchanged, **at this gate**.
- `docs/CHECKLIST_SCHEMA.md` — gate `g3-schema` owns it.
- `scripts/collect_feedback.py` (#464), `episodes/` (#460),
  `scripts/verify_worktree_precondition_coverage.py` (#436) — concurrent sibling issues this wave.
- The gate schema itself.

## Constraints the Implementation Must Respect

- `_render_directive_lines`'s docstring must name the corpus shapes it was verified against, as
  `_render_anchor_lines`'s does. An unrecognized shape renders nothing rather than guessing.
- The test's leaf extraction must not be shared with the renderer's — a shared bug would render
  nothing and assert nothing, in agreement, and both sides would report green.
- No new dependency.

## Map Anchors (inbound)

Inherited from `g1-implement`. Verify the change against the same anchors:

- **Structural:** `scripts/checklist_engine.py` — `state()` ~1588, `_render_anchor_lines()` ~1650,
  `render_human()` ~1667; `tests/test_checklist_engine.py` — `GoldenOutputBriefing` ~3779.
- **Capability:** the projection is the complete state channel (`docs/agents/GLOSSARY.md`) — agents
  drive from what `current` prints, never from the JSON file.
- **Constraints/assumptions:** `assumption:schema-type-is-drifted` — `docs/CHECKLIST_SCHEMA.md`
  declares `directives` as `[string] | null`; all 8 populated corpus instances are dicts. The renderer
  serves the corpus; the document is corrected at g3. Do not BLOCK on the document disagreeing.
- **Decision anchors:**
  - `decision:render-not-delete` `@grade: settled/measured · leans g1`
  - `decision:own-helper-not-anchors-helper` `@grade: settled/human · leans g1`
  - `decision:goldens-written-before-the-change` `@grade: settled/inherited · leans g1`
- **Evidence expectations:** `claim:a-populated-directives-block-appears-in-current`, proved over the
  real shipped template rather than a fixture shaped like it.
- **Map confidence flags:** no `docs/architecture` map exists in this repo; orientation is DEGRADED by
  standing condition. `docs/CHECKLIST_SCHEMA.md` is known stale on the `directives` row.

## Evidence Produced (reproduce it, do not accept it)

- RED capture: `.agent-work/b433-render-directives/evidence/g1-RED-capture.txt` —
  `5 failed, 2 passed, 339 deselected, 4 subtests passed`, `EXIT=1`, with `checklist_engine.py`
  asserted UNCHANGED in the same invocation.
- Post-change: `346 passed, 30 subtests passed`, `EXIT=0`.
- Wiring grep: 2 lines outside the definition, 1 a real call site (`render_human()` ~1771), 1 a comment.
- The implementer notes the shipped `execute` gate carries **six** contract fields, not the four its
  handoff's abbreviated example showed; the golden was written over the real six.

## Suggested Model Tier

**Stronger.** The load-bearing check is a RED you must reproduce by mutating the tree and restoring it.

## Stop Conditions

Return BLOCK if: the diff cannot be accessed; the RED cannot be reproduced; evidence is absent or
unverifiable; an excluded file was touched; or a policy decision is needed before a verdict.

## Return Format

Return REVIEW_RESULT with an explicit `verdict:` line reading exactly `APPROVE` or `BLOCK`, then
per-check findings (one per close criterion, each with how you verified it), blockers, out-of-scope
observations, and workflow feedback.

Write it to:
`C:/Programs/constellation-skills-wt/r418-433/.agent-work/b433-render-directives/crew-handoffs/g1-review-REVIEW_RESULT.md`

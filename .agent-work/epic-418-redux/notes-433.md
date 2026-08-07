# notes-433 — issue #433, render `directives` in the `current` projection

Delegated Commander, worktree `C:/Programs/constellation-skills-wt/r418-433`, branch
`epic-418/b-433-render-directives`. Launch order: `.agent-work/epic-418-redux/launch-orders/LO-433.md`.

## Isolation proof (first command, before any git operation)

```
$ python scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/r418-433
worktree OK: in C:/Programs/constellation-skills-wt/r418-433
EXIT=0
```

## Pre-declared subsumption candidate set — filed BEFORE the first code change

Drawn from the three theme labels the launch order names. Ten candidates. Each gets a
disposition at the triage step; declining one is fine, declining it silently is not.

From `theme:checks-that-cannot-fail`:

1. **#392** — consolidation candidate: "a check that cannot register its own failure", deferred by #308.
2. **#382** — negative control: aliased-import defeat, and an artifact-ref one-element fixture that lets
   truncation pass. Same vacuity family as this issue's completeness property.
3. **#384** — `default_repo_state`'s `dirty: None` half is a surviving mutant.
4. **#372** — reopens' conceded amend-drop under-count is reachable but pinned by no test.
5. **#292** — installer refusal tests assert only a non-zero exit.

From `theme:engine-mechanics`:

6. **#390** — `amend` can add/drop/rescope and retext checks, but no op can supersede a clause inside an
   existing imperative. Adjacent: `directives` is the structured channel prose duplicates.
7. **#457** — spine rail attributes a descendant's gate to its ancestor. (LO records it live and unfixed.)
8. **#311** — document the `!` negation-wrapper pattern inline in `IMPLEMENTER_PLAN.template.json`.

From `theme:built-not-wired`:

9. **#345** — pattern: this project reliably builds capability and unreliably delivers it, six instances in
   one epic. A populated `directives` block the engine never renders is one more instance of that shape.
10. **#458** — no checkable answer to "is this project constellation ready"; the governor ships nowhere.

## Inventory — what the corpus's gates actually carry in `directives`

Enumerated by command over every JSON file in the worktree carrying a `tasks` map
(`$CLAUDE_JOB_DIR/tmp/inv.py`, walked at branch head), so the count is derived, not remembered:

```
total gates scanned: 2955
  null: 2947
  dict: 8
POPULATED directives: 8 gates across 8 files
  skills/commander/templates/COMMANDER_SPINE.template.json :: execute  :: dict :: ['replan_input']
  skills/admiral/templates/ADMIRAL_SPINE.template.json     :: execute  :: dict :: ['wave_transition']
  skills/explorer/templates/EXPLORER_SPINE.template.json   :: confirm  :: dict :: ['shaped_brief']
  .agent-work/epic-418-redux/spine.json                    :: execute  :: dict :: ['wave_transition']
  .agent-work/b433-render-directives/spine.json            :: execute  :: dict :: ['replan_input']
  (+ 3 copies of the same three templates under .agent-work/archive/)
```

**Verdict: render, do not delete.** Three reasons, in order of weight:

- It is carried by **three shipped spine templates** and therefore by every Commander, Admiral and
  Explorer run instantiated from them — including this run's own spine. Not vestigial.
- `tests/test_iterative_planning_doctrine.py` asserts the parsed contract in all three templates
  (`directives["replan_input"]`, `["wave_transition"]`, `["shaped_brief"]`), so a consumer exists.
- Every populated instance is a **dict of contract fields**, not the `[string]` the schema's Task table
  claims. The schema type is drifted; the render must handle the shape the corpus really carries.

Nothing reads `directives` at engine runtime: `grep -rn directives scripts/ skills/` returns only the
`amend` op plumbing (`checklist_engine.py:2052,2166,2264`) and two `None` initializers. The contract text
survives only as prose restated inside the same gate's `imperative` — which is exactly why the structured
block being invisible was never noticed.

---

# Execution log — successor Commander

The predecessor tripped the context governor at the `plan` seam, filed a refresh-request against
`w-3`, and stopped correctly. A fresh Commander took over the same spine, same lease, same
`why_trail` — no analysis was redone. It resolved the pending refresh by advancing `plan`, then drove
`execute` through `g1` and `g2`.

## What shipped

**g1 — the field renders.** `scripts/checklist_engine.py`: `state()` passes `directives` through
beside `constraints`/`anchors` (one line, no coercion, no check re-run); a new
`_render_directive_lines()` with a `_directive_leaf()` scalar speller sits beside
`_render_anchor_lines()`; `render_human()` emits the block between `anchors:` and `next:`. Both live
shapes are served — key-to-nested-contract-dict (all 8 populated corpus gates) and flat list of
strings (what the schema declares and the `add` amend op accepts). Absent, empty and unrecognized add
zero output. `tests/test_checklist_engine.py` gained `class RenderDirectives`, goldens authored over
the **actual shipped** `COMMANDER_SPINE.template.json` `execute` gate.

**g2 — the class is closed by a property that can fail.** `class TaskFieldCompleteness`:
`directives` removed from `_EXCLUDED_FIELDS` (the other 13 exclusions keep their stated per-entry
reasons); `_flatten` replaced by a total recursive `_leaf_texts`; the single `checked_any` flag
replaced by a **per-field ledger** whose failure message names the offending field; a new test
asserting the fixture's key set is a **superset of the engine's own `_build_amend_task` output**; and
an in-suite **negative self-test** that drives the real assertion path against a render with
`directives` stripped and asserts the raise names the field.

**Carry-over from the g1 review**, folded into g2: `_render_directive_lines`'s flat-list branch was
silently dropping non-string items — the fix reproducing its own defect class in miniature. Made
total, with a test.

## The finding the predecessor paid for, confirmed in execution

Un-excluding `directives` alone would have produced **a check that cannot fail**. `_flatten` returned
`[]` for the nested-dict shape, so the inner loop body never ran and the property asserted nothing
while reporting green. Red-proof R2 reproduces exactly that world and now fails loudly.

The deeper hole, from cold-critic finding 1, is the one that actually closes the class: the loop runs
over the **fixture's** keys, so a field added to the engine and forgotten in the fixture was absent
from the loop, absent from the ledger, and green. Red-proof R5 pins that shut.

## Red-proofs — reproduced three times over, by three different agents

| proof | world it recreates | result |
|---|---|---|
| R2 | extractor returns `[]` for dicts (the old `_flatten`) | ledger set-mismatch naming `anchors`, `directives` — EXIT=1 |
| R4 | a populated field that flattens to nothing | fails **by name** — EXIT=1 |
| R5 | a field added to `_build_amend_task`, not to the fixture | superset assertion fails **by name** — EXIT=1 |

Produced by the implementer, independently reproduced by the cold reviewer, and R4 reproduced a third
time by the Commander in its own hands
(`.agent-work/b433-render-directives/evidence/g2-integrate-commander-red-reproduction.txt`). The g1
red was likewise reproduced by the Commander with the engine reverted to HEAD and the goldens left in
place (`evidence/g1-integrate-commander-red-reproduction.txt`).

## Subsumption — dispositions against the pre-declared set of ten

**Closed: 0 of 10.** A visible number, and the honest one. Nothing in this issue's scope touched any
of the ten; each is declined here rather than silently dropped.

| # | candidate | disposition |
|---|---|---|
| 1 | #392 consolidation candidate: a check that cannot register its own failure | **declined — adjacent, not subsumed.** This issue fixed one instance of the family in one test class. #392 is about the engine's own consolidation path. |
| 2 | #382 aliased-import defeat + one-element artifact-ref fixture | **declined.** Same vacuity family; different mechanism and different file. The per-field ledger pattern here is a candidate *technique* for it. |
| 3 | #384 `default_repo_state`'s `dirty: None` surviving mutant | **declined.** Untouched by this scope. |
| 4 | #372 reopens' amend-drop under-count | **declined.** Untouched. |
| 5 | #292 installer refusal tests assert only a non-zero exit | **declined.** Untouched. |
| 6 | #390 no `amend` op supersedes a clause inside an imperative | **declined, but materially informed.** `directives` is exactly the structured channel the imperative prose duplicates; now that it renders, relocating instruction text into it is possible — that is workstream C's job, not this issue's. |
| 7 | #457 spine rail attributes a descendant's gate to its ancestor | **declined.** Live and unfixed; no rail change here. |
| 8 | #311 document the `!` negation-wrapper inline in the plan template | **declined.** No template change here. |
| 9 | #345 built-not-wired pattern | **partially served, not closed.** This was one more instance of the shape, and it is now wired: the `_render_directive_lines` wiring grep found a real call site, and the completeness property is the standing check against the next instance *within Task fields*. The pattern issue stays open. |
| 10 | #458 no checkable answer to "is this project constellation ready" | **declined.** Untouched. |

## Triage candidates raised during execution (not filed — the Admiral's call)

1. **`append()` and `_build_amend_task` duplicate the Task shape by hand.** The new superset
   assertion reads only the latter, so a field added to `append()` alone stays invisible. One shared
   constructor removes the class. Raised independently by the g2 implementer and the g2 reviewer.
2. **A template-only Task field is invisible to the superset assertion.** This is the residual limit
   the class docstring states — and it is live, not theoretical: **`anchors` is emitted by neither
   builder**. A check walking shipped templates' task objects for keys neither builder emits would
   close it.
3. **Nothing checks `docs/CHECKLIST_SCHEMA.md`'s Task table against the builder.** Such a check would
   have caught the stale `directives` row by itself.
4. **The `CONTEXT` gauge advisory is read from the checklist file's directory**, so a crew's own plan
   inherits the Commander's gauge. A crew agent that obeyed it would hand off on turn one. Observed by
   the g1 implementer at 11% on its first `claim`.
5. **The engine mints a work-area directory keyed on `work_id` beside the plan, not under it**
   (`.agent-work/b433-render-directives-g1-implement/`). Both crew roles hit it in one gate.
6. **An untested defensive branch** in `_render_directive_lines` (dict value that is not a dict).
   Proved dead by mutation — replacing it with `raise` leaves the suite green. Non-blocking; kept
   deliberately, same posture as `_render_anchor_lines`'s unrecognized-shape return.
7. **The flat-list branch's silent drop** — found by the g1 reviewer, **fixed in g2**, listed here
   because it is the clearest evidence the defect class is real: it appeared inside the fix for it.

## Workflow feedback harvested from the crews

- **The reviewer skill and the workbench dogfooding reference conflict on which engine copy drives a
  review of the engine itself.** Both crews hit it; the g2 reviewer's case is the sharpest — close
  criterion 3 required it to *break* the vendored engine mid-review. Both chose the installed copy so
  their own survey state could not be corrupted. Neither document anticipates "the engine you drive is
  the engine you break." This deserves a named paragraph.
- **`--session-id` is required on every mutating verb after `claim`**, and that is stated in neither
  the implementer skill nor `global-everyone.md` §Engine verbs. The g1 implementer learned it from
  three consecutive refusals.
- **Templates hardcode `config_ref: docs/agents/engine-config.json`.** Independently reported by the
  g2 implementer and the g2 reviewer as a field that looks load-bearing and is not. Per LO-433 this is
  a Charter deliverable and has been filed twice already (#443, #462, both closed) — **recorded here,
  deliberately not filed a third time.**
- **Line numbers in map anchors go stale within a run.** g1's insertion moved `TaskFieldCompleteness`
  from ~3958 to ~4192, and the g2 handoff's pointer was already wrong when it was written. Anchors into
  a file the same run edits should name symbols, not lines.
- Both handoffs drew the same criticism from opposite ends: an abbreviated example next to a
  "match the ACTUAL shipped thing" refusal condition (g1), and a red-proof set numbered R2/R4/R5 with
  no R1 or R3 and no note saying why (g2). Show the full artifact, or label the abbreviation.

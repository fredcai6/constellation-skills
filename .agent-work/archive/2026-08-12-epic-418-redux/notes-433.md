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

## Execution log — third Commander (successor at the `g2-integrate` seam)

Took over after the second dispatch tripped the governor's HARD band at `g2-integrate` and filed
`e-g2-integrate-3`. Cold-started from the engine's `current` on the existing `spine.json` and
`execute.json`; reused the lease `commander-b433-render-directives` and the existing `why_trail`.
No committed work redone.

### What this dispatch actually did

1. **Independent verification of the inherited g2 result** — did not take APPROVE on trust.
   Broad suite: 1731 passed / 4 skipped / 647 subtests, `REAL_EXIT=0`. Then re-derived a red-proof
   from scratch (nulled the `directives` passthrough in `state()`): the completeness property failed
   naming the field, with `constraints:`/`anchors:` still rendered in the same failure message —
   direct evidence that no field covers for another. Tree restored byte-identical
   (`git hash-object` `ef979b43…` both sides). Capture:
   `evidence/g2-integrate-successor-commander-verification.txt`.

2. **g3-schema** — both doc corrections, verified against the gate's pre-authored command
   postconditions (c1/c2 exit 0), plus the broad suite (c3, exit 0). Capture:
   `evidence/g3-schema-doc-correction.txt`.

3. **Resolved the carried g1-reviewer finding.** The STATE_NOTE warned that a separate sentence at
   `docs/CHECKLIST_SCHEMA.md:138` asserts `directives` "is not rendered" and that c1's negation would
   not catch it. On inspection that is the **same sentence** that carries "Known gap" — one sentence
   held both claims — so c1's conjunction does catch it, and no amendment to c1 was needed. Verified
   by grepping the whole file for `not rendered` / `never surfaced` / `known gap` / `directives`: the
   only surviving `directives` mentions (lines ~237, ~288, ~290) are handoff and amend-op references
   that were already accurate. Recording this because the warning was a real risk correctly raised —
   it just resolved in the benign direction on inspection rather than by assumption.

### Governor finding — worth an issue

`gauge.json` held the SECOND dispatch's reading (0.184143, `observed_at` 00:03:06Z) and nothing
refreshed it, because `scripts/hooks/gauge_writer_hook.py` is not wired into this worktree's
`.claude/settings.json` (the known-open #180 wiring). A fresh dispatch therefore inherits its
predecessor's exhaustion and is blocked by it at every `advance`.

Two exits were available and both were refused as dishonest: hand-writing a gauge record (forging the
instrument the governor reads) and filing a refresh-request for a context exhaustion this dispatch was
not experiencing (a false statement in the journal, and a fourth dispatch for nothing). Instead: do
all the gate work, which needs no `advance`, and let the reading age out of `gauge_reader`'s
30-minute window on its own — the degradation `docs/GAUGE_WRITER_HOOK.md` explicitly designs for
("writes nothing and leaves the existing file to age into staleness"). Advance then proceeded
normally.

**Triage candidate (new, #11):** a stale gauge reading survives the session it describes. Either the
reader should discount a record whose writing session is gone, or a fresh dispatch should be able to
invalidate an inherited reading through a sanctioned verb — not by hand-editing the file. Today the
only honest path is to wait out a 30-minute timer, which is a real tax on every relaunch and quietly
rewards the dishonest shortcuts.

### Triage routed — all nine candidates FILED to the tracker (not banked)

The notes above said "not filed — the Admiral's call". The third dispatch filed them instead, for two
reasons stated so the Admiral can overrule cleanly: LO-433's Inherited Latitude floats *closing* an
issue but not *filing* one, and the spine's triage step gives delegated mode an explicit path to
satisfy c2 by citing that latitude. Banking findings worktree-locally for later harvest is also the
exact habit Tommy has corrected three times.

| # | candidate | issue |
|---|---|---|
| 1 | `append()`/`_build_amend_task` duplicate the Task shape | #474 |
| 2 | template-only field invisible to the superset assertion (`anchors` is one **today**) | #475 |
| 3 | nothing checks the schema doc's Task table against the builder | #476 |
| 4 | the gauge is read per checklist dir, so a crew inherits the Commander's reading | #477 |
| 5 | crew work areas minted beside the plan, not under it | #478 |
| 6 | dead defensive branch in `_render_directive_lines` (kept deliberately) | #479 |
| 7 | the flat-list silent drop — fixed in g2, filed as the record | #480 |
| 8 | a stale gauge reading outlives its session | #481 |
| 9 | reviewer/dogfooding conflict: the engine you drive is the engine you break | #482 |

#475 is the one to read first: it is the only candidate that shows the field class #420 and #433 both
attacked is **still open today**, by name.

### Workflow feedback — third dispatch's own reflection

**Followed closely:** the spine, gate order, and every pinned postcondition. Nothing was improvised
around a frozen check; where a check refused (`attest execute.c1` — engine-checked, `advance
reconcile` — gate still pending) the refusal was correct and the fix was to use the right verb.

**Where I had to improvise, and it was a real gap:**

1. **The inherited gauge reading.** Covered at length above and filed as #481. The mechanism has no
   honest fast path for a fresh dispatch, only a 30-minute wait. That is the single biggest workflow
   defect this run hit.
2. **`REPLAN_INPUT.json` did not exist**, despite the execute imperative saying it should be written
   "as execution proceeds". Two predecessors both ended without it, which suggests the instruction is
   easy to defer past — it sits mid-paragraph in a very long imperative and has no gate of its own
   until the step's exit. Authoring it retroactively is possible but weaker: the discrepancy
   classifications are reconstructed rather than recorded live.
3. **The G2 packet's shape is not discoverable from the template alone.** The template shows
   `completed_outcomes: []`, so its required field set (`issue_id`/`outcome`/`evidence`) and the
   partition rule (completed ∪ open must exactly equal the wave's issue ids) are only learnable by
   reading `verify_replan.py`. Same for `diagnosis` in the episode delta, where the template implies a
   dict and the writer requires a list of `{kind, ...}`. Two refusal round-trips each.

**Contradiction, carried up rather than resolved:** LO-433 says do not edit `episodes/`; the spine's
`feedback` step requires writing episodes through `apply_episode_delta.py`, whose only target is
`episodes/`. I followed the spine (the writer is the sanctioned write path and I hand-edited nothing),
but a sibling Commander is retiring `episodes/` under #447, so **these three new episode files may
collide with that retirement.** Flagging rather than deciding — the Admiral owns the sequencing.

**Not a 'none' answer:** confirmed after review of the two crew REVIEW_RESULTs, the two IMPLEMENTER
RESULTs, and the g1/g2 fowler passes.

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

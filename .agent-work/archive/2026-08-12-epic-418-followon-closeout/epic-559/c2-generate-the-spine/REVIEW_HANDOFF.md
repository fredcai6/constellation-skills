# Cold reviewer handoff — C2 rework: seven blockers, and a wave where four reviews each missed something

**Work id:** `epic-559/c2-generate-the-spine` · **Gate:** `rework-review` · **Role:** reviewer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine` (branch `epic-559/c2-generate-the-spine`)
**Under review:** the rework working tree against `main`, and the whole branch as an integration.
**Deliverable:** `.agent-work/epic-559/c2-generate-the-spine/REVIEWER_RESULT.md`

You are **cold**. The rework is good work and I am not asking you to confirm that.

## Read this first — four reviews in this wave, four different misses

This branch has already been reviewed four times. Every reviewer ran real commands. Every one
answered its own questions correctly. Each missed something anyway:

1. **g1** round-tripped a deliberately awkward pytest selector through the oracle's own parser and
   declared the property held "under adversarial-shaped input." It stress-tested the field that was
   **already quoted**, while `min_collect: 2` sat untested in the same call. It missed a field that
   was never quoted — **invisible because absent**.
2. **g2 round 1** verified `hand_back_to` was present on all 9 gates and passed it. The value was a
   stale Admiral session id.
3. **g2 round 2** did the same and wrote the stale id verbatim into its own evidence line as proof of
   completeness — **invisible because ubiquitous**. 9-of-9 read as deliberate.
4. **g3** structurally diffed regenerated against driven output, wrote that the regenerated file
   "still carries the original, broken text," then classified it as expected provenance and approved.
   It **saw** the defect, **described it accurately**, and scoped the question away.

The pattern: **a review establishes that a mechanism operates and does not ask whether the value it
operates on is right.** Absence and ubiquity both read as correct. Our doctrine's three-way guard
fixture covers absence; nothing covers a value that is wrong but consistent.

**So for every check, ask two questions, not one: does this mechanism work, and is the value it
carries correct?** The second is where four reviews died.

## What the rework claims

Seven blockers. Four fixed, one deliberately floated, two out of scope and reported:

- **Blocker 0 (TDD):** a `pytest` kind gains an opt-in `not_yet_written` declaration. Generation
  reports `undecidable-pytest-not-yet-written` instead of a fault. It compiles to `check: null`.
- **Blocker 1:** `min_collect`, `expected`, `expected_min`, `expected_max` now refuse a non-integer
  (`spec-non-integer-field`).
- **Blocker 2:** VIOLATING/INNOCENT fixtures, 34 new test methods in 4 classes.
- **Blocker 4:** the shipped specs' `parent` becomes a placeholder, with a VIOLATING-proven guard.
- **Divergence:** fixed at the **source** spec, never the generated spine.
- **Large claim on a survey:** driven on a real survey host, still does not fire on
  `record`/`consolidate`, reported unfixed as out of scope.
- **Dispatch flags:** reported as triage; `run_crew.py` is owned by another workstream.

Suite: **2823 passed, 3 skipped**. Baseline on `main` is 2689/3.

## The questions that decide the verdict

**`v1` — is the TDD escape hatch actually closed?** `not_yet_written` compiles to `check: null`. A
gate whose *only* postcondition is such a declaration must still be refused, or this field is a
general-purpose way to author a gate that cannot fail — the exact defect the generator exists to
prevent, now with a supported keyword. The Admiral drove this: a single-condition `not_yet_written`
gate is refused by `falsifiable-all-null` with nothing written. **Reproduce that, then attack it.**
Try to build *any* spec that uses `not_yet_written` to reach a written spine with no check that can
ever fail. Multi-gate, mixed kinds, qualitative paired with it — whatever you can think of. If you
find one, that is a BLOCK and the most important finding on the branch.

**`v2` — the four numeric fields, both directions.** Confirm each refuses a non-integer and that a
valid spec's compiled output is byte-identical to before. Then ask the g1 question properly: **is
there any remaining author-controlled value that reaches a compiled shell command without being
quoted or typed?** The crew enumerated its answer in `IMPLEMENTER_RESULT.md`. Do not confirm its
list — derive your own from the source and compare.

**`v3` — the crew reported a defect in its own new code.** `not_yet_written` is read with bare
truthiness (`cond.get("not_yet_written")`), so a string `"false"` is truthy and misread as a
declaration. It named this and left it, arguing out-of-scope. Judge that call. Say whether shipping a
new field with a known misreading is acceptable or is a BLOCK.

**`v4` — the divergence fix.** The source `dispatch-proof/probe.spine.toml` was corrected; the
generated `dispatch-proof/spine.json` was deliberately left as the completed run's audit trail. Check
that regenerating from every source spec now reproduces its committed artifact, or that any remaining
difference is a stated audit-trail exception rather than a fresh divergence.

**`v5` — the stale parent.** It is now a placeholder with a guard. Verify the guard **fires** on a
session-specific literal (write one and watch it refuse) and does not fire on the placeholder. Three
reviewers passed this value; do not be the fourth.

**`v6` — the sweep must be unmoved.** `python scripts/validate_spine.py --sweep --root .` must still
report exactly **23** fault lines. Any change means a shipped template moved.

Standard items apply: scope held, no hard no-gos touched, suite green, evidence reproducible.

## Known, and not yours

- **The large-claim escalation does not fire on a `survey`.** Measured and reported honestly; the
  generator refuses to inject a postcondition the engine will never consult and states the
  non-enforcement in the rendered gate. Do not re-litigate the design; do confirm the statement it
  renders is true.
- **`DESIGN_NOTE.md` §4/§7/§10 are stale** against shipped behaviour. The crew named this rather than
  silently leaving it. Triage, not a blocker.
- **`run_crew.py` dispatch flags** belong to `epic-559/g1-model-record`, in flight now.
- **`validate_spine.py` is frozen** — it is the oracle. The crew floated a request to extend it rather
  than patching it, which is correct. The Admiral rules on that, not you.

## Hard no-gos the change was under

`scripts/checklist_engine.py`, `scripts/validate_spine.py`, `scripts/run_crew.py`, `settings.json`,
`docs/agents/*`, and every shipped template under `skills/*/templates/` untouched. No merge or push
to `main`. Confirm each.

## Test mode

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Use `python`, not `python3`.

## Drive your own work through the door

Your dispatch binds `SPINE_FILE`/`SPINE_SESSION` and names your parent in `SPINE_PARENT`. Use
`mcp__spine__*`, found via `ToolSearch`. A check you cannot satisfy means `spine_halt block` and a
return — never a waive, which is denied for crews anyway.

## Verdict

`APPROVE` or `BLOCK`, with evidence you personally ran. An honest partial is acceptable; a silent gap
is not. Write `.agent-work/epic-559/c2-generate-the-spine/REVIEWER_RESULT.md`, including **Workflow
Feedback**, before ending your turn — that write is the delivery.

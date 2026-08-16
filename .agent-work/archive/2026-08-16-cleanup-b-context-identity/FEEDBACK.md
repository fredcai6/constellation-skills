# Feedback — leg 3, `cleanup-b-context-identity`

Honest reflection before the episodes, as the gate asks.

## How closely the skills, handoffs and checklists were followed

Closely, with one deliberate departure and one near-miss.

**The departure:** the `g1-review` gate imperative was frozen before
`ADMIRAL_RULING-2.md` existed, so its check (d) demanded behaviour the Admiral
had since amended. Following it literally would have made the reviewer block on
something already ruled correct. The ban on hand-editing `execute.json` mid-run
is absolute, so the amendment was **relayed through the reviewer handoff**
instead, with the superseded clause named explicitly. That is the seam the
doctrine leaves open — handoffs are writable, frozen gates are not — but nothing
in the skill says "use the handoff to carry an amendment the gate cannot", and it
took a deliberate decision to find it.

**The near-miss:** merging `main` invalidated two instructions in the
already-written reviewer handoff — the diff range (`git diff a69bbac4` would have
handed the reviewer lanes C and D as this lane's work) and the suite baseline.
`LAUNCH_ORDER-3.md` said to dispatch "with the already-written handoff", and
doing that literally would have produced a review of the wrong diff. Caught only
because the merge and the handoff were read together.

## Where instructions had to be worked around

- **`--session-id` on every mutating verb.** Refused three times before it stuck.
  Both crews reported the same friction independently. Three agents in one wave
  losing a cycle to one missing line is a doc gap, not three mistakes.
- **`git mv` on untracked files.** The packet sweep half-succeeded: tracked
  packets moved, this leg's new ones failed with "not under version control".
  Re-run with plain `mv`.
- **The state-note verifier takes a positional work id, not `--work-id`,** while
  the sibling `verify_iterative_role_artifacts.py` takes `--work-id`. Two
  neighbouring scripts, two conventions.

## What was ambiguous, missing or contradictory

- **`completed_outcomes` in `REPLAN_INPUT` partitions against *issue* ids**, not
  gate ids, and the template's example does not make that visible — its
  `completed_outcomes` is empty. The first packet listed gate ids and was
  refused. The refusal message was precise and the fix was quick.
- **"Retire the probe" vs "update the probe".** The state note and leg 2 digest
  said *retire*, naming a replacement; the gate imperative said *update it so the
  archived artifact no longer misdescribes the fixed world*. The gate won, being
  the operative instruction, but the two readings differ in what ships.
- **The engine's guarded-gate instruction says "close it and stop"**, which reads
  as one gate per leg. Four guarded gates were closed here, each with its own
  `refresh-request`. That is a defensible reading of "this gate" but it is a
  reading, not what the text plainly says.

## What would have helped

- **An evidence standard that asks whether the new branches are covered.** The
  implementer handoff rightly warned about patched readers, injected
  `CLAUDE_PROJECT_DIR` and stale bytecode — but never asked "show a mutation that
  turns each behavioural row red". The single finding of this whole review sits
  exactly in that gap. The reviewer names it too.
- **A way to record a ruling amendment against a frozen gate**, so the next
  Commander does not have to rediscover the handoff seam.

## Crew Workflow Feedback harvested

From the `g1-review` crew (the `g1-implement` crew's was harvested by leg 2):

- The `SessionStart` misfire is **real and reproducible** — the reviewer's
  environment carried the parent's `SPINE_FILE` **and** `SPINE_SESSION`. It notes
  the reviewer skill's own wording ("do not author a survey of your own when a
  spine is already bound") points a compliant crew straight at the wrong spine,
  and that **the handoff's closing warning is what saved the run**.
- `advance` is refused on a `survey` checklist; `record` is the advancing verb,
  which the skill's step 3 gets wrong.
- What the handoff got right, in its words: telling it the diff range had moved,
  and **separating the whole-file fences from the in-file `claim`-path fence** —
  that separation is what made it AST-extract the claim path rather than eyeball
  hunks.
- Suite figures should state **the tree and the unit**: three totals circulate in
  this lane (3057, 3089, 3104) and its freshly measured `main` also landed on
  3089 — the same number as a stale figure, for a different tree.

## A "none" answer that needed checking

No gate was skipped for convenience and no evidence was fabricated —
**confirmed** by re-running the reviewer's own commands rather than trusting
them, by driving the probe in both directions against a real pre-fix worktree,
and by measuring both suite sides at gate time instead of quoting either
inherited figure.

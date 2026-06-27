# The Delegated/Autonomous Commander — Design

**Issues:** [#34](https://github.com/fredcai6/constellation-skills/issues/34) (sanctioned
autonomous-dispatch mode + verify-from-artifacts on commander idle) and
[#36](https://github.com/fredcai6/constellation-skills/issues/36) (commander-spine
papercuts: dead compact step, reasoning-gate crew waiver, crew survey-state location).

**Date:** 2026-06-27

## Problem

`constellation-commander` is written as the human's **rigor scaffold** — it "surfaces
decisions to the human rather than making them." But under an Admiral it is routinely
driven **autonomously**, on a harness where a dispatched subagent **cannot reach the
human**, and nothing sanctions that reading. Four threads, all tracing to skill/template
text that assumes a reachable human or a crew per gate:

- **#34a — no autonomous mode (story_time `commander-spine-mismatch-for-autonomous-dispatch`).**
  The `understand` step's Interrogator "must reach the human"; `plan`/`triage`/`review`
  pause for `user-decision` checkpoints; gates launch nested `run_crew.py` crews. None fits
  an autonomous subagent under a run-to-completion Admiral, so the Admiral abandoned the
  Commander skill and re-derived a bespoke single-agent implementer every run.
- **#34a — delegated user-decision checkpoints (f1Brainz `delegated-context-user-decision-checkpoints`).**
  Under a wave where the human pre-froze scope, the `user-decision` postconditions are
  correctly satisfiable by citing the frozen launch order — but the skill text has no
  documented reading for that, so each run improvises it.
- **#34b — idle commanders drop their verdict (story_time `admiral-verifies-from-artifacts-on-commander-idle`).**
  An Agent-tool commander sometimes ends with only an `idle_notification`
  (`idleReason: available`) and never emits its verdict text — hit 2 of 4 reporting
  commanders. Work was complete (artifacts were ground truth), but a future Admiral could
  hang waiting for a message that never comes.
- **#36 — three spine papercuts (f1Brainz singles).** (1) `compact-step-agent-uninvokable`:
  the spine `compact` step runs `/compact`, a user-level CLI the agent cannot invoke, so
  every run skips it with reason — a permanent dead step. (2) `reasoning-mission-crew-gate-mismatch`:
  the execute gate mandates implementer/reviewer crew dispatch for **every** gate, even pure
  design-note/diagnosis gates where the Commander already holds the context and a crew would
  be **shallower**. (3) `crew-survey-state-in-worktree-root`: a crew reviewer's survey-checklist
  state (`.agent-work/g1-review/review.json`) was created at the **worktree root**, leaving
  orphan untracked scratch that closeout had to hunt down.

## Strategy

**Express every behavior as a documented reading / convention of the existing spine — no
new engine fields, gate markers, or spine variants.** This is mechanically sufficient: the
engine already accepts a `user-decision` artifact regardless of who authored it, already
accepts attested (`check: null`) postconditions, and already lets the Commander author the
gate shapes it needs. So all five fixes are skill/template/doctrine text, with **zero engine
code**. This matches the fold-back arc's posture (#32/#33/#35 each chose the no-new-machinery
path): a `mode: autonomous` field or a `mode: reasoning` gate marker would be enforcement
surface the field has not yet shown it needs, and would create two modes to maintain.

Autonomous mode is **not** a licence to guess. A genuine decision outside the Commander's
inherited latitude still **floats to the Admiral** (per the launch order's Stop Conditions
and the latitude contract's float-up routing) rather than blocking on an unreachable human —
the human's reachability moves up one tier, it does not vanish.

## Behavior

### A. Delegated/autonomous mode — `commander/SKILL.md` + `COMMANDER_SPINE`

A new **"Delegated/autonomous mode"** section in `skills/commander/SKILL.md` (after "Human
checkpoints (rigor dial)", which it qualifies). Contents:

- **Trigger.** Running from an Admiral `LAUNCH_ORDER` **is** the delegated signal: the human
  is not directly reachable this run; the Admiral is the human's delegate and the frozen
  launch order is the ratified scope.
- **`understand` reading.** The Interrogator's "must reach the human" is read as **reconcile
  the ask against the frozen launch order** (Mission, Pre-Rulings, Inherited Context,
  Inherited Latitude) as the source of truth. An open question the launch order does not
  answer and that exceeds inherited latitude is **floated to the Admiral** per the launch
  order's Stop Conditions — not guessed, not blocked on the human.
- **`user-decision` checkpoints.** The four `user-decision` postconditions (`understand` c1,
  `plan` c3, `triage` c2, `review` c1) are satisfied in delegated mode by **attaching a
  `user-decision` evidence item that cites the governing launch-order section** (e.g. via the
  engine `attach`/`attest` path), with the Admiral as ratifying authority and the human
  ratifying at the epic return boundary. The engine is unchanged — it already only requires a
  `user-decision` artifact to be present; the citation rides in the evidence payload for
  audit. Interactive (human-driven) runs are unchanged.

The four spine steps' imperatives (`understand`, `plan`, `triage`, `review` in
`skills/commander/templates/COMMANDER_SPINE.template.json`) each gain a brief clause: "In
delegated mode (running from an Admiral launch order), satisfy this checkpoint by citing the
frozen launch order — see the commander skill's *Delegated/autonomous mode*." No structural
change to the spine (same items, same postconditions, same `user-decision` checks).

### B. Verify-from-artifacts on commander idle — `fleet-doctrine.md` + `admiral/SKILL.md`

Extends the existing "Adjudication invariants (Admiral errors that bit)" section of
`skills/admiral/references/fleet-doctrine.md` with one invariant: **artifacts are ground
truth; a verdict message is a convenience an idle Agent-tool commander can silently drop.**
When a dispatched commander returns only an `idle_notification` (`idleReason: available`)
with no verdict text, the Admiral **verifies from the artifact set** (branch / commit / PR /
changed files) and a **clean-room reviewer subagent** pointed at those artifacts, and
**never blocks waiting on a verdict message**. This dovetails with the existing
"confirm-dead-before-you-touch-its-worktree" and "issue-close-gates-on-verified-MERGED"
invariants. `skills/admiral/SKILL.md`'s Execute-doctrine bullet on a Commander that "dies or
stalls" gains a pointer: an **idle** commander with complete artifacts is *done*, verified
from artifacts — not a stall to wait on. Doctrine only; no script (the clean-room is a fresh
reviewer subagent, which the Admiral already knows how to dispatch).

### C. Compact step — `COMMANDER_SPINE` `compact`

Reframe the `compact` step `imperative` from the unconditional "Run /compact to compress
conversation context" to **conditional**: ensure context headroom for the execute phase —
run a compaction command **if your harness exposes one**, otherwise note that harness
auto-compaction covers it — and **always reload the constellation-commander skill** into this
context and confirm it is active. The skill-reload is the load-bearing half (post-compaction
the skill text may be evicted) and stays mandatory; the harness-specific `/compact`
invocation becomes conditional so the step stops being a permanent skip-with-reason ceremony.
The step keeps its place, items (c1/c2), and `check: null` attestations; only the imperative
wording changes (c1 reads "context headroom ensured (compaction run if available, else
auto-compaction noted)").

### D. Reasoning gate — `commander/SKILL.md` "Executing a gate"

Document a sanctioned **reasoning-gate** reading in the commander SKILL's "Executing a gate"
section: a gate whose deliverable is a **document or diagnosis**, and whose context the
Commander already holds, may be authored **crew-less** — without the `gN-implement` /
`gN-review` crew dispatch — and driven in the Commander's own context, with the **waiver
reason stated in the gate**. Its closeout postcondition is an **attested** (`check: null`)
or `user-decision` artifact (in delegated mode, cited from the launch order) rather than a
crew `review-result`. The rule of thumb: a crew on a pure design note is **shallower**, not
safer; reserve crew dispatch for gates that produce code or an independently-verifiable
change. This is an alternative gate **shape the Commander already has the freedom to author**
(`execute.json` is authored per-run); the doctrine makes it sanctioned and discoverable.

`skills/commander/templates/EXECUTE_PLAN.template.json` is **not** edited: it is strict JSON
(the suite `json.load`s it) so it cannot carry an explanatory comment, and adding a second
gate variant would clutter the canonical implement→review→integrate example. The reasoning-gate
shape is documented in the SKILL prose, which is its proper home; the template stays the single
crew-gate example.

### E. Crew survey-state location — `REVIEWER_HANDOFF` + `reviewer/SKILL.md`  *(isolated, 36.3)*

The Commander knows the `work-id`; the reviewer does not pick a good path on its own. Add a
**"## Survey State Location"** field to `skills/commander/templates/REVIEWER_HANDOFF.template.md`
giving the exact path the reviewer must create its survey checklist at:
`.agent-work/<work-id>/<gate>-review/review.json`. Add a matching clause to
`skills/reviewer/SKILL.md` (where it says to drive the survey through the engine): **create
the survey checklist under the issue workbench at the path given in the handoff — never at the
worktree root**, so closeout finds no orphan untracked scratch. Scoped to the crew
survey/checklist state the incident named; not a broader scratch-location refactor.

## Testing

All changes are documentation/template text — **no engine code, so no unit tests** (mirrors
#32/#33's doc tasks and #35's Task 2, which were review-gated). Gates:

- **Review against this spec.** Each component's named files carry exactly the reading above,
  with no stale "the interrogator must reach the human" / "Run /compact" absolutes left
  unqualified and no contradiction between the new commander-skill sections and the spine
  imperatives.
- **JSON validity.** `COMMANDER_SPINE.template.json` (the only edited `.json`) must still
  parse (`py -c "import json; json.load(open(...))"`) after editing — the sole mechanical
  check. (`EXECUTE_PLAN.template.json` is not edited; see component D.)
- **Full suite stays green** (222 passed / 1 skipped on this branch's base — it forks from
  main, independent of the open #35 PR): the template-loading tests are the regression guard
  that the JSON edits did not break a shipped template.

## Out of scope (YAGNI)

- **No `mode: autonomous|interactive` field, no `mode: reasoning` gate marker, no separate
  autonomous spine.** The documented reading is mechanically sufficient; markers are
  unmaintained surface until the field asks.
- **No verify-from-artifacts script / no engine change.** The clean-room is a reviewer
  subagent; artifact inspection is ordinary git.
- **No collapsing the Commander into a single-agent implementer.** Autonomous mode keeps the
  gate structure; leanness comes per-gate from reasoning gates, not from dissolving the
  Commander's role. (The Admiral's choice of *how heavy a unit to dispatch per issue* is
  existing Admiral dispatch latitude, not part of this change.)
- **No broad scratch-location refactor for 36.3** — only the crew survey/checklist state the
  incident named moves under the work-id workbench.
- **No new `user-decision` evidence subtype.** A delegated checkpoint uses the existing
  `user-decision` evidence type; the launch-order citation is payload content, not a schema
  change.

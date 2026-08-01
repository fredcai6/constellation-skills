# Excursion X1 result -- resume-block inventory (THIN vs RICH)

## The one named question
For a fresh/resumed constellation agent at each tier (implementer, reviewer,
commander, admiral), how much of a cold-start "resume block" is ALREADY
provided by durable engine + handoff state today, and what is MISSING that a
context-governor handoff would still have to supply?

## Scope

**Examined:**
- Installed skills (`C:/Users/fredc/.claude/skills/`): `constellation-implementer`,
  `constellation-reviewer`, `constellation-commander`, `constellation-commander-delegated`,
  `constellation-admiral`, `constellation-workbench` -- `SKILL.md`, `templates/`, `references/`.
- Repo source (`C:/Programs/constellation-skills`): `scripts/checklist_engine.py`
  (full read of the verb/session-lease/journal machinery), `scripts/verify_state_note.py`,
  `scripts/run_crew.py` + `scripts/recover_crews.py` (docstrings + key sections),
  `skills/_shared/global-everyone.md`, `skills/workbench/references/checklist-engine.md`,
  `skills/admiral/references/fleet-doctrine.md`, `skills/commander/references/commander-core.md`.
- Templates: `IMPLEMENTER_HANDOFF`, `REVIEWER_HANDOFF`, `IMPLEMENTER_PLAN`, `REVIEW_SURVEY`,
  `COMMANDER_SPINE`, `ADMIRAL_SPINE`, `EXECUTE_PLAN`, `MISSION_FRAME`, `LATITUDE_CONTRACT`,
  `LAUNCH_ORDER`, `STATE_NOTE`, `ADMIRAL_LOG`, `WORKFLOW_CLOSEOUT`, `INTERROGATION` /
  `INTERROGATION_RECORD`.
- `crash-resume` / `resume` / `reopen` doctrine: grepped across all installed skills and the
  repo; read every hit in `fleet-doctrine.md`, `global-everyone.md`, `verify_state_note.py`.
- The exploration's own `IDEAS_BOARD.md` for the framing this excursion answers into.

**NOT examined (explicit scope-out):**
- `docs/CHECKLIST_ENGINE_DESIGN.md` (model rationale) -- only `docs/CHECKLIST_SCHEMA.md` was
  spot-checked for the `evidence`/`status_detail` field shapes.
- The full `checklist_engine.py` line-by-line (1517 lines) -- read fully for `current`,
  `attach`, `release`, the journal sidecar, and the rail-string mechanism; other verbs
  (`amend`, `waive`, `reopen`, `record`, `consolidate`) read only via `checklist-engine.md`'s
  prose description, not their own code.
- `constellation-commander-delegated`'s own `SKILL.md` (only `commander-core.md`, which it
  binds to, was read), and `constellation-cartographer`/`constellation-lessons-auditor`
  (out of the named tiers).
- No live run was inspected -- no real `spine.json`/`crew-runs.json` from a genuinely crashed
  session was read; the `.agent-work/dispatch-126-127/harvest*` trees under this repo were
  located but not opened (they are installed-skill copies bundled inside eval fixtures, not
  live spine state). Everything below is claimed from **doctrine and template shape**, not
  from observing an actual crash-resume.
- No hands-on test of the engine (`current`, `claim`, `attach`) was run against a live file --
  this is a read-only doctrine/template inventory, not an executed drill.

## Two distinct "resume" situations, conflated by the tier list

The doctrine draws a real line the per-tier table below preserves:

1. **Stalled-but-alive** (the process/session still exists): `fleet-doctrine.md`'s Recovery
   drill says resume it directly via the harness's session-continue primitive -- "full context"
   survives, because it is the same conversation. This is **not a cold start** and a
   context-governor handoff is irrelevant to it (this is the case the governor's own project
   is aimed at replacing -- deliberately handing off *before* a crash, not after one).
2. **Confirmed-dead / genuinely fresh** (host exit, box reboot, no live PID, or a brand-new
   agent taking the role for the first time): "resume from the engine's on-disk spine/execute
   state -- do not restart from zero." This is the actual cold-start case the named question is
   about, and where a governor's payload would land.

The inventory below is written for case 2.

## Per-tier inventory

### Implementer

**Reconstructs, and from what:**
- The bounded task itself -- task, protected intent, test mode, close criteria, allowed scope,
  specific exclusions, constraints, map anchors, deliverable path check, required evidence,
  verification commands, authority, stop conditions -- from `IMPLEMENTER_HANDOFF.md`, a file
  the Commander wrote and which is durable on disk (not engine state; a plain committed/local
  file the handoff explicitly classifies).
- Which plan item is active, its status, and its (generic, template-authored) imperative -- from
  `IMPLEMENTER_PLAN.json` via the engine's `current` verb, if that file already exists at its
  fixed work-area path.
- Evidence already attached to completed items (command output, attested facts) -- from the same
  plan file's per-task `evidence[]` array.
- The actual code/diff already produced -- from the git working tree itself (durable, outside
  the engine entirely).
- **Primary crash-resume path is CLI session-continue**, not artifact reconstruction:
  `run_crew.py`/`recover_crews.py` classify a dead attempt as `resumable` and resume it by
  session name (same transcript) when possible; only a non-resumable attempt is fully
  relaunched with the original handoff.

**Gap -- what it does NOT reconstruct:**
- No mandated "why" trail. `attach`'s evidence payload is an arbitrary key/value bag the agent
  chooses to fill; nothing forces a rationale for a judgment call made mid-step, so any
  reasoning not yet promoted to an `evidence` item at the moment of death is gone.
- In-step work-in-progress: anything after the last `advance`/`attach` and before the crash --
  "I was about to try X because Y" -- has no durable slot at all. The plan file only records
  *completed* postcondition satisfaction, not partial in-flight state.
- No implementer-tier equivalent of `STATE_NOTE.md` -- the crash-resume state-note gate (`p2`
  in the spine) exists only on the Commander/Admiral spines, not on `IMPLEMENTER_PLAN.json`.
  A dead implementer crew has no first-class "step/slug/next-command/pid/expected-artifact"
  note; recovery instead depends on the Commander-owned `crew-runs.json` registry, which is
  process/session bookkeeping (pid, backend, result path), not a narrative resume block.
- On full relaunch (non-resumable case), whether the relaunched crew *reuses* the partially
  advanced `IMPLEMENTER_PLAN.json` or starts a fresh plan file at the same path is not settled
  by anything read -- the skill's "Start here" instructions say "build a `gated` plan" without
  naming existing-file detection. Scoped null: **not tested** against real engine behavior.

**Verdict: RICH-leaning THIN.** The handoff file already carries almost everything a governor
would want to hand a fresh implementer (it *is* essentially a hand-authored cold-start block),
and the plan file adds completed-step evidence on top. The real gap is narrow but real:
no mandated rationale capture, no state note for this tier, and no fresh-vs-resume disambiguation
rule for the plan file.

### Reviewer

**Reconstructs, and from what:**
- Everything the implementer's handoff gets, reviewer-shaped -- what was implemented, how to
  inspect the diff, task statement, close criteria, allowed scope, exclusions, constraints, map
  anchors, evidence produced -- from `REVIEWER_HANDOFF.md` (durable file, Commander-authored).
- Per-check pass/fail + findings already recorded -- from `REVIEW_SURVEY.json`'s per-task
  `finding`/`result` fields via `current`, at whatever path the handoff's "Survey State
  Location" names (`.agent-work/<work-id>/<gate>-review/review.json`).
- The Fowler-pass record (flagged/overridden/absent per code smell, with logged override
  reasons) -- from `FOWLER_PASS.template.json` once written, a separate durable artifact.
- Crash/resume mechanics identical to implementer: CLI session-continue when alive-classified,
  full handoff relaunch when not.

**Gap -- same shape as implementer, plus:**
- A survey is explicitly append-and-visit-every-item with **no blocking on failure** -- so a
  resumed reviewer must re-derive which checks are genuinely done vs which were recorded `fail`
  but not yet acted on; the survey state does not distinguish "still needs a human eye" from
  "recorded and accepted as a finding."
- No state note either; same reliance on Commander-owned `crew-runs.json`.
- Reproduced-evidence doctrine ("a claim you cannot reproduce is a BLOCK finding, not an
  accepted fact") means a resumed reviewer must **redo** reproduction work already done before
  the crash unless that reproduction's raw output was itself attached as evidence -- the survey
  does not require the reproduction transcript, only the pass/fail verdict.

**Verdict: RICH-leaning THIN** -- same reasoning as implementer.

### Commander

**Reconstructs, and from what:**
- The full 10-step spine position (`init -> context -> understand -> plan -> execute ->
  reconcile -> triage -> review -> feedback -> archive`), status per step, and each step's own
  imperative -- from `spine.json` via `current`. This is the richest single artifact in the
  corpus: it names the exact next imperative text, not just "you're on step N."
- Session-lease ownership and staleness -- from `spine.json`'s `engine_session` block; a resumed
  session `claim`s idempotently and inherits the lease cleanly.
- The frozen gate plan with per-gate map anchors (`structural`/`capability`/`constraint`/
  `decision`/`evidence`/`confidence_flags`) -- from `execute.json`, authored once at `plan` and
  never hand-edited afterward (only `amend`/`reopen` touch it, both logged).
- The mission frame (intent, affected capabilities, structural anchors, governing
  constraints/decisions, map confidence flags, out-of-scope) -- from `MISSION_FRAME.md`, a
  durable file produced before `execute.json` is authored.
- The exact detach point -- step, slug, next command, PID, expected artifact -- from
  `STATE_NOTE.md`, **mechanically enforced**: `execute`'s precondition `p2` refuses to enter
  the detach-heavy phase until the note is filled (`verify_state_note.py`), and doctrine says
  "when honored, every recovery was a clean resume from the note."
- Crew dispatch/recovery state (which implement/review crews are done, running, resumable,
  dead) -- from `crew-runs.json` via `recover_crews.py`'s classifier.
- Human checkpoint answers -- from `user-decision` evidence items attached at `understand`,
  `plan`, `triage`, `review` (interactive: a real confirmation; delegated: a launch-order
  citation).
- An append-only, hash-chained provenance journal (`spine.json.journal`) recording every
  successful mutating verb (seq, timestamp, session id, verb, task, evidence ids) -- this is
  **tamper-evidence for audit**, not designed as a human-readable narrative; it lets a resumed
  session (or a reviewer of the run) confirm the sequence really happened, but carries no
  rationale text.
- In delegated mode specifically: `LAUNCH_ORDER.md` is explicitly written as a from-scratch
  cold-start block ("Commanders start cold. Paste, don't point.") -- mission, pasted (not
  linked) prior-wave verdicts, pre-rulings, honest-null clause, inherited latitude, file
  ownership, workspace, inherited context (a "Charter-lite carrier" when the target repo has no
  `docs/agents/` overlay), pre-empted spine steps, data locations, budget, stop conditions,
  return shape. This is functionally a governor-shaped handoff already, but it is authored
  **once, at initial dispatch**, not regenerated at a mid-run refresh seam.

**Gap -- what it does NOT reconstruct:**
- **No synthesized "current understanding" that updates mid-run.** The mission frame is frozen
  at `plan` time; nothing re-derives or updates a running summary as `execute` proceeds. A
  resumed commander must reconstruct "what have I learned since planning" by re-reading
  `execute.json`'s accumulated evidence and the crew results by hand -- there is no single
  running digest artifact.
- **In-progress-step partial reasoning is not captured** -- same gap as implementer/reviewer,
  scaled up: mid-gate deliberation ("I was about to adjudicate this BLOCK by...") that had not
  yet become a spine `attach`/`advance` is lost on a genuine crash.
- **`STATE_NOTE.md` is a discipline, not an invariant**, outside the first write: the engine
  only guarantees the note *exists* before the first detach; keeping it *current* across every
  subsequent detach (the PID changes each time) is explicitly named as "your discipline," not
  mechanically enforced -- so a stale note is a real, doctrine-acknowledged failure mode
  ("the one time it was skipped, ~3h vanished to forensics").
- **The interrogation transcript is not guaranteed durable.** The `understand` step attaches
  the *consolidated* problem statement as `user-decision` evidence; the raw interrogation
  survey (`interrogation.json`, with each question's `fact`/`decision` typing and
  `code_evidence`/`human_answer`) is a separate file whose retention/archival was not confirmed
  read -- nuance in the back-and-forth may not survive to a resumed session unless that file is
  independently preserved.
- **Rework/waiver rationale is present but thin by construction**: a `waive` requires
  `--reason`, and a `reopen` supersedes evidence (retained, not deleted) -- so *that* something
  was overridden is durable, but *why the human accepted the risk* beyond the one-line reason
  string is not.
- **A refresh-at-a-chosen-seam mechanism doesn't exist at all today.** Everything above is
  built for two situations -- normal step-to-step advance, and crash recovery -- never for a
  voluntary "I'm getting full, hand me off now" mid-gate seam. There is no template for "what a
  Commander mid-`execute`, three gates deep, would package for its own fresh successor absent a
  crash" -- that payload does not exist in the corpus today.

**Verdict: THIN, with one clearly-scoped RICH gap.** The spine + mission frame + execute.json
anchors + state note already cover *most* of a mechanical cold-start ("where am I, what's the
plan, what happened so far, what map context governs it"). The genuinely missing piece is a
**running, mid-execute synthesized digest** and a **voluntary refresh-seam payload** -- neither
exists; both would be new governor-owed content, not something re-derivable from what is already
durable.

### Admiral

**Reconstructs, and from what:**
- Epic spine position (`init -> latitude -> execute -> closeout`) and each step's imperative --
  from `spine.json`, same mechanism as Commander.
- The negotiated authority boundary -- epic intent, success shape (incl. honest-null
  acceptability), checkpoint protocol, decision classes (surfaced vs delegated), permission
  prerequisites, float-up routing, comms style, budget/model parameters, pre-rulings, expiry --
  from `LATITUDE_CONTRACT.md`, durable and explicitly re-confirmed on expiry/ground-shift.
- **The run's full narrative audit trail** -- `ADMIRAL_LOG.md`, explicitly the "run's audit
  trail and the lessons audit's primary input," with a fixed entry grammar (`RULING`, `WAVE`,
  `INCIDENT`, `MERGE`, `ADMIRAL ERROR`, `CHECKPOINT`, `ESCALATION`) and the doctrine "append
  entries as they happen -- an unlogged ruling didn't happen." This is the one artifact in the
  whole corpus explicitly designed as human-readable resume narrative, not just machine state.
- Crash-resume state note (step/slug/next-command/pid/expected-artifact) before every detached
  wave launch -- same mechanism and same enforcement/discipline split as Commander.
- Per-Commander dispatch state -- worktree paths, branch names, launch orders issued -- logged in
  `ADMIRAL_LOG` as `WAVE` entries (the doctrine specifically calls a provisioned worktree "a
  material fleet action" that must be logged).
- Closeout state -- lessons audit disposition, reconcile status, hygiene sweep, summary
  acceptance -- from `WORKFLOW_CLOSEOUT.md`, though this is a Commander/workbench-level
  artifact; the Admiral's own closeout is folded into `spine.json`'s `closeout` step
  postconditions plus the `ADMIRAL_LOG`'s own Closeout section.

**Gap -- what it does NOT reconstruct:**
- Same missing pieces as Commander (no running mid-execute digest, no voluntary refresh-seam
  payload, state-note currency is discipline not invariant) -- Admiral inherits every Commander
  gap because it is built on the same spine/engine primitives.
- **Cross-Commander synthesis is not automatic.** ADMIRAL_LOG records each wave's dispatch and
  each Commander's returned verdict as logged entries, but nothing mechanically rolls up "what
  is the epic's current net state across N Commanders" into one artifact -- a resumed Admiral
  reconstructs that by reading the whole log plus every affected worktree, not from one
  pre-digested summary.
- **The sleeper hazard is explicitly named as unresolved by any artifact**: "you cannot tell
  done / sleeping / dead apart from the status alone -- inspect the worktree + PID." No durable
  state answers this; it is a required manual drill every time, which is itself evidence the
  existing artifacts do not fully solve cold-start ambiguity at this tier.
- **Worktree isolation state is not durable** either -- it is a harness no-op on Windows the
  Admiral must re-verify itself per Commander, not something reconstructable from any artifact.

**Verdict: RICH artifact coverage for narrative/audit, but same structural gap as Commander.**
ADMIRAL_LOG is the strongest evidence in the whole inventory that "durable narrative resume
state" is achievable and already partly built -- but it is an append-only log a resumed agent
must *read in full and re-derive from*, not a pre-digested handoff block, and it inherits every
gap named at the Commander tier.

## Overall verdict: MIXED, leaning THIN with one recurring, well-scoped RICH gap

Across all four tiers, the **existing engine + template state already reconstructs**: identity
of the current step and its full instruction text (`current`), the frozen plan/handoff content
(task, scope, criteria, constraints, map anchors -- all durable files, not chat memory),
completed-step evidence, session/lease ownership, and (for Commander/Admiral) an exact
detach-point note plus, for Admiral, a genuine human-narrative audit log. This is substantially
more than "nothing" -- a governor riding entirely on top of it would not be starting from zero
at any tier.

What is **consistently missing, at every tier**, and would be a governor's real payload:
1. **In-flight/partial reasoning capture** -- nothing durable holds a step's working state
   between its last `attach`/`advance` and a crash or voluntary handoff.
2. **A running, synthesized "current understanding" digest** -- every tier's durable state is
   either frozen-at-authoring (mission frame, latitude contract, handoffs) or an append-only
   log/plan a resumed agent must re-read and re-derive from; nothing pre-digests it.
3. **A voluntary refresh-at-a-chosen-seam artifact** -- every existing mechanism is built for
   either normal advance or crash recovery; none is built for "I'm not dead, I'm choosing to
   hand off now." This is the literal shape of the governor's own stated goal, and it does not
   exist today at any tier.

If the governor's job is narrowly "make crash-resume clean," the engine/handoff state already
does most of that work and the governor would be thin -- closer to codifying/enforcing what
already exists (e.g. making `STATE_NOTE.md` currency mechanical rather than discipline) than
inventing new payload. If the governor's job is "give a *voluntarily* refreshed fresh agent a
cold-start block as good as a live-context agent," none of the four tiers has that today, and
the payload -- the mid-flight digest plus the refresh-seam handoff shape itself -- is new
content the governor owes at every tier alike.

## Scoped nulls

- This inventory rests on doctrine/template text, not on an executed drill: no real spine was
  driven through a crash and resumed to observe actual `current` output, actual journal
  contents, or actual crew-registry classification in practice. The claims above about *what
  the engine would print* are inferred from `checklist_engine.py` source and
  `checklist-engine.md`/`fleet-doctrine.md` prose, not measured.
- Whether a relaunched (non-resumable) implementer/reviewer crew reuses or overwrites a
  partially-advanced plan/survey file at the same path was **not tested** -- flagged inline
  above as a named gap in what was examined, not a settled fact either way.
- `constellation-commander-delegated`'s own `SKILL.md` was not read directly (only the shared
  `commander-core.md` it binds to) -- any commander-delegated-specific doctrine layered on top
  of `commander-core.md` is out of scope for this pass.
- No comparison was made against `constellation-cartographer`, `constellation-lessons-auditor`,
  or other non-named-tier skills' resume behavior -- the four named tiers only.

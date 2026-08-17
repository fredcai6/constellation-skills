# Run feedback — `cleanup-f-derive-worktree` (#609 lane F)

Five episodes are the durable record (`episodes/active/cleanup-f-derive-worktree-001`
…`-005`, tracked in git). This file carries the reflection the episode grammar
does not hold: how closely the run followed its instructions, where it improvised,
and what the crews said about the handoffs they were given.

## How closely the run followed the skills, handoffs and checklists

**Closely, with two departures, both recorded rather than quiet.**

1. **Reconcile repaired six sites where the order named three.** The extra three
   are the same claim family, falsified by this lane's own `g2`, found by grepping
   the claim rather than opening the named files. Justified by the Admiral's own
   rule — *the change that falsifies a claim owns the repair* — and named in the
   return, the triage record (T22) and the replan packet (D28) rather than folded
   in silently. All prose; no executable line moved.
2. **Two gates were begun over the context governor's line.** The engine's
   documented sequence — request the refresh, `start` the pending active gate,
   `advance --why` — was followed exactly, and both are in the trip ledger as
   `begin-instructed` (`tl-6`, `tl-8`). In both cases the gate's whole substance
   was done, attested and committed **before** the gate was begun, so the start
   began no work it could not finish.

## Where I had to improvise

- **The governor's refusal reads as terminal and is not.** I wrote a handoff and
  nearly parked a leg on that misreading, one gate after the previous leg parked
  on the same one. What corrected it was reading the engine's own comment and the
  trip ledger underneath the refusal, which already showed refuse-then-instruct
  twice. Episode `-005`.
- **`archive.c2b` and the launch order disagree.** The postcondition requires an
  OPEN or MERGED PR; the order reserves publication to the Admiral. I did not
  improvise past it — see the archive step's record.
- **The crew registry reports a correctly-parked leg as `failed`**, because the
  result artifact's status is `partial`. I recorded it (D22) rather than working
  around it by mislabelling my own return.

## What was ambiguous, missing or contradictory

- **A prose repair scoped by a file list is what let three stale claims survive.**
  The launch order and `ADMIRAL_RULING-3` each named the files to repair, and both
  lists were built by a reader who had gone looking. Grepping the *claim* instead
  found six sites of one family across five files; the three no list named were
  falsified by this lane's own `g2`. The rule belongs beside the citation rule
  (*cite by the string to grep for* — `LAUNCH_ORDER-5`): **scope a prose repair by
  the claim family, not by the file list**, and grep a fragment short enough to
  survive line wrapping, because the site that no symbol-keyed check could find was
  the one whose claim wrapped across two comment lines. `ADMIRAL_RULING-5` confirms
  the diagnosis — the list was the defect, not carelessness in following it.
  Episode `-004`.
- **Two different findings on this lane are both called `tc1`** — `execute.json`'s
  is the empty `map/ids.jsonl`, the launch order's is the SessionStart scan-bind.
  Survey `flag-candidate` ids restart per file, so this will recur (T7). The
  triage record opens with the warning and routes by content throughout.
- **`CREW_SCRATCH_DIR` is not scrubbed** by the engine's own gate-close suite
  command, while a Commander is itself launched through `run_crew.py` (T12).
- **The reconcile imperative assumes a packet map.** This repo has none, and
  `map/ids.jsonl` is zero bytes, so every Commander here orients
  DEGRADED-UNPARSEABLE (T1). The imperative's second path — reconcile the
  structural record directly — is what made the step closable.

## What would have helped

- A list, at plan time, of what `_foreign_worktree` was **incidentally
  preventing**. That one list was worth four rework cycles.
- A shared claim-family sweeper. The eight-line `sweep_claims.py` a crew wrote
  under `.agent-work/` is the tool three gates needed and each re-invented (T8).
- Knowing before the first suite run that watching a run changes it (T11).

## Harvested crew Workflow Feedback

From the `g3` reviews, `gN-integrate` by `gN-integrate`:

- **The handoff field that did the most work** was *reproduce their instrument,
  then go past it*, paired with a concrete list of what "past" meant — three or
  more matches, mixed attribution, the acting session owning one of the matches.
  Naming the topologies beat saying "be thorough".
- **Advice reached the next crew through a result artifact rather than a
  handoff.** Review 4 said criteria 1–5 were one parameterised matrix; that never
  made it into review 5's handoff, and review 5 rebuilt the matrix only because it
  read its predecessor's result. Promote a predecessor's closing advice into the
  successor's Close Criteria.
- **The Fowler record path** must be per-crew; the template's single path collides
  once a gate has more than one reviewer, and nine variants now sit in this work
  area. Two consecutive reviews reported it (T7).
- **`flag-candidate` ids collide across surveys** — four different findings called
  `tc1` on one work id (T7).
- **A hazard list should name the store's real filename.** The reviewer lost a run
  finding `.spine-rail-binding.json` rather than `binding.json`, and lost another
  discovering that an end-to-end case-fold construction requires hand-writing one
  binding key, because no production writer can emit a case variant on a
  case-sensitive host.
- **Engine friction, minor and self-correcting:** a survey checklist has no
  `advance` — `record` is the advance — and the engine's refusal message is what
  taught the reviewer. The message is good.
- **Nine crews received the `SPINE MID-FLIGHT` nudge for a spine they did not
  own, refused it, and recorded the refusal.** None was penalised and none wrote
  to this spine. That is the behaviour working, and the mechanism is T13.

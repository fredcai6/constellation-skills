# Issue #377 — Problem Statement (consolidated)

## Standing authority
This run cannot reach a live human (background job; explicit constraint "you cannot
ask the user anything"). The **commander brief + admiral pre-rulings ARE the human
decision of record**. The `understand` and `plan` user-decision gates are therefore
attested against the brief, not an interrogation. Logged per override mechanics.

## The ask (WRITE-UP ONLY)
Carry the fusion-rework UNDERSTANDING from qualifying to race-start and race. Produce
ANALYSIS + ONE DOCUMENT (`docs/evo/fusion_task_generalization.md`). Build NOTHING:
no `src/` or `scripts/` changes, no committed measurement infra. Existing
scripts/diagnostics may be run read-only; archived artifacts may be read. Throwaway
analysis snippets allowed only under `.agent-work/`.

The user framing: "let's see how quali goes and then we'll make a call." This write-up
is the INPUT to that later call and to #392's cross-module consolidation pass. It is
not itself a build decision.

## Three threads (acceptance)
1. **Validate the diagnosis PER TASK (don't average).** The redundancy facts
   (driver↔constructor collinear; recent↔weekend ~independent) were characterized on
   quali. Read them off per-task diagnostics + the #373 harness for race_start and
   race. Three sub-questions: (a) does constructor dominate MORE on race? (b) is
   recent↔weekend independence preserved downstream or does it collapse once you
   condition on the prior stage's order? (c) does "A moves calibration not ordering"
   hold per task?
2. **Stage-specific interaction hypotheses + conditioning variables for #374/#375.**
   The #140 "weekend vs form disagreement ⇒ upgrade" story is a qualifying-PACE
   hypothesis. race_start (lap 3): launch/getaway, grid-position-dependent first-lap
   chaos, (prior quali-order × start-performance). race: degradation/strategy/tyre
   management — compound-regime (push vs race-pace β/γ crossover) as the natural
   conditioning signal; plus overtaking difficulty and (prior-order × pace). Both
   downstream stages receive the prior stage's order as a handoff ⇒ the richest
   interactions likely involve prior-stage-order × pace-deviation, a structure the
   quali probe doesn't have. Also: what is the race/race_start ANALOGUE of #414's
   "the head ignores cross-channel pace evidence" — does an information-not-calibration
   deficit plausibly exist downstream, and what would anchor it?
3. **Ceiling-aware prioritization.** Persistence baselines: grid→lap3 0.875,
   lap3→finish 0.776, grid→finish 0.753; downstream modules already AT these ceilings
   ⇒ race_start persistence-dominated (little headroom), race has more. Use
   `scripts/diagnose_prediction_ceiling.py` to set per-stage expectations.

## Deliverable structure (admiral pre-ruling 2)
`docs/evo/fusion_task_generalization.md` (new; sole owner): plain-English executive
summary first, then Thread 1 / Thread 2 / Thread 3, then "Inputs to the #375
conditioning design" and "Inputs to #392 (cross-module consolidation)".

## Hard constraints
- Do NOT touch `docs/evo/fusion_rework_findings.md` (#374 owns it) or
  `docs/evo/prediction_ceiling_and_priorities.md`.
- Every number traces to a named artifact (scorecard.json, findings docs, a logged
  script run). Thin evidence / speculation must be LABELLED. "The quali story does
  NOT generalize" is a complete successful deliverable.
- REQUIRED before PR: one independent reviewer crew that re-derives every cited number
  and flags any claim stronger than its evidence.

## Protected intent
The honest map. A sparse honest read beats a dense confident one. The doc feeds a
human's later go/no-go on extending the fusion rework downstream — overclaiming
generalization would mislead that call.

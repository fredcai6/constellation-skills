# Commander: native CLI workflow

## Contents
- [Role](#role)
- [Checklists you own](#checklists-you-own)
- [How it works](#how-it-works)
- [Executing a gate](#executing-a-gate)
- [Repo](#repo-default-charter-overrides)
- [Human checkpoints](#human-checkpoints-rigor-dial)
- [Modes: interactive and delegated](#modes-interactive-and-delegated)
- [Decision candidates](#decision-candidates)
- [Mission frame](#mission-frame)
- [Architecture bookend](#architecture-bookend)
- [Templates](#templates)

## Start here — drive the engine before you touch the problem

You were engaged to **run** an issue, not to solve it by hand. The moment this skill loads — before you read the issue closely and before you write a single line of solution code — do this, in order:

1. **CLAIM the engine lease on the spine you were handed.** The worktree, `.agent-work` directory, and `spine.json` already exist by the time this skill loads — the dispatcher (the Admiral for a delegated run, the human for an interactive one) stood them up per `references/stand-up-work-area.md` before handing you the spine path. Your job is not to build any of that; it is to `claim` the checklist lease with the engine on the spine.json you were given. This is your **first command**, ahead of any problem-solving.
2. **Ask the engine what to do next, at every step.** Run the engine's `current` verb, do exactly what the active step's imperative says, and `advance` only once its postconditions pass. Never skip ahead, and never hand-write or hand-edit `spine.json` — the engine owns that state and stamps the provenance (session lease, heartbeats, evidence) that proves the work was really driven.
3. **Deliverables come out of the spine, not around it.** `solution.py`, its tests, and the completion artifact are produced **inside** the gated steps (plan → execute → …), gated by the engine — never written first and backfilled into the spine afterward.
4. **Producing the solution is the MIDDLE of the run, not the end.** When an implementer crew hands back `solution.py` and green tests, you are still at the `execute` step — **not done**. Integrate the result, `advance` execute, then drive **every** remaining spine step (reconcile → triage → review → feedback → archive) through the engine. **Do not end your turn while any spine step is still `pending` or `in-progress`:** run the engine's `current` verb and keep going until the final `archive` gate is ready. The single most common failure at this tier is stopping the moment the code exists — resist it. At `archive`, satisfy or waive every postcondition and complete the commit, episode, push, and PR prerequisites while the lease stays active. Then call `spine_close` once with `tree_clean=true`, `episodes_captured=true`, explicit `push` and `open_pr` choices, and a `why` value unless the close is mechanical. That one bound-spine call releases declared child plans, advances and releases the top-level lease, reaps bindings, and archives the work area. Do not manually call the final `spine_advance` or `spine_lease release`; those steps now belong to `spine_close`.
5. **Dispatching a crew is never a reason to end your turn.** If you run headless: ending your turn to "wait for the crew" means nothing resumes you — the run just dies mid-`execute`, no matter how well the crew is doing. When you dispatch an implementer or reviewer and must wait for its result, wait **actively, inside your turn**: poll the crew's result artifact (or registry) in a loop until it lands, then integrate it and drive on. Treat the thought "I'll wait for it to finish" as the cue to **start polling**, never to stop and yield.

**Work the engine never saw did not happen.** A run that solves the issue directly, or copies the spine template and never advances it, or hand-writes a spine that merely *looks* complete, or **drives the engine only as far as the solution and then stops**, has **failed this dispatch** no matter how correct the answer — the deliverable of a Commander run is a spine driven all the way to a terminal `archive`. Write the completion artifact only after the `archive` step has released the lease.

## Checklists you own

Commander drives three checklists in sequence:

| Checklist | Template | When |
|---|---|---|
| `spine.json` | `templates/COMMANDER_SPINE.template.json` | Entire run — the fixed workflow |
| `interrogation.json` | (Interrogator drives it) | The `understand` step; load Interrogator in this context |
| `execute.json` | `templates/EXECUTE_PLAN.template.json` | Authored at `plan`; driven as frozen at `execute` |

Once authored, `execute.json` is never **hand-edited** mid-run — that ban stands. When a gate proves the plan wrong, change it through the engine, not the JSON: use the `amend` verb (a validated delta that adds/drops/rescopes **pending** gates and records reason + authority) to re-plan the gated tail, and `reopen` (which cascade-resets downstream gates and supersedes their evidence) when a closed gate's work must be redone. Either way, surface the decision to your principal before continuing.

## How it works

Drive the gated spine (`templates/COMMANDER_SPINE.template.json`) through the engine one step at a time: **init → context → understand → plan → execute → reconcile → triage → review → feedback → archive**. The template holds the exact instructions.

| Step | Where it runs |
|------|--------------|
| understand | this context — load `constellation-interrogator`; interactive: the Interrogator reaches the human, else (delegated) reconcile against the launch order — see "Modes" |
| plan | this context — author `execute.json` using `templates/EXECUTE_PLAN.template.json` |
| execute | this context — first ensure context headroom (compaction if the harness exposes it, else auto-compaction) and reload this skill, then drive `execute.json` gate by gate |
| reconcile | subagent — load `constellation-cartographer` |
| triage | this context — load `constellation-triage`; each candidate routes to `fixed-now`, `filed`, or `recommend-and-defer` — fix-now dispatches crew within the authorized latitude |
| review | this context — summarize run, get principal acceptance |
| feedback | this context — reflect on the run, then record what happened as episodes and apply them via `scripts/apply_episode_delta.py` (the only write path; never hand-edit under `episodes/`), proved by `scripts/verify_episode_captured.py` |
| archive | this context — satisfy commit, episode, push, and PR prerequisites, get the human's final acceptance of the archived run, then call the bound `spine_close` lifecycle tool once |

The common `Intake and boundary evidence` obligations run at `understand` on this path. Use `scripts/verify_spec_confirmed.py` for the validator route. For bounded probes, fill the existing `../constellation-prototyper/templates/PROTOTYPE_HANDOFF.template.md`, dispatch through `references/crew-dispatch.md`, and integrate `../constellation-prototyper/templates/PROTOTYPE_RESULT.template.md`. This uses the existing understand gate and prototype contract; add no new fields or spine step.

## Templates

`templates/COMMANDER_SPINE.template.json`, `templates/EXECUTE_PLAN.template.json`, `templates/MISSION_FRAME.template.md`, `templates/IMPLEMENTER_HANDOFF.template.md`, `templates/REVIEWER_HANDOFF.template.md`. Engine: `references/checklist-engine.md`. Crew dispatch: `references/crew-dispatch.md`.

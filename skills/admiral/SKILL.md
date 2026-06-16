---
name: constellation-admiral
description: Run an epic as the human's delegate — confirm latitude, dispatch Commanders in waves, adjudicate and merge, close with lessons and architecture audits. Use when handed work spanning multiple issues.
---

# Constellation Admiral

Run one epic end to end as the human's delegate. The Admiral **never commands an issue itself**: it dispatches Commanders, adjudicates what they float, merges their results, and logs every ruling. Rigor concentrates at the bookends — latitude in, lessons out — and the middle is free.

**Mandatory, no exceptions: drive the spine through the engine. Within the execute step, judgment is yours — when an instruction does not fit the epic, do the closest compliant thing and report the misfit at closeout; reporting misfit is compliance, not deviation.**

## Spine

Drive `templates/ADMIRAL_SPINE.template.json` through the engine: **init → latitude → execute → closeout**.

| Step | What happens |
|---|---|
| init | work area for the epic id; claim the engine session lease |
| latitude | load `constellation-interrogator`; produce and confirm the latitude contract |
| execute | dispatch waves, adjudicate, merge — free middle, log mandatory |
| closeout | lessons audit, map reconcile, repo hygiene, epic summary, user acceptance |

## Latitude (first bookend)

Before anything launches, settle how much rope you have. Load `constellation-interrogator` and fill `templates/LATITUDE_CONTRACT.template.md`: epic intent and success shape (honest-null acceptability), checkpoint protocol, **decision classes** (which choices you may adjudicate vs. must surface), float-up routing for Commander `user-decision`s, comms style, budget/model parameters, pre-rulings, and an **expiry** (time or event). The contract is the dial between "I don't care, go" and "float me the details" — get it confirmed by the human before wave 1.

A decision that fits no listed class is **out-of-taxonomy and always escalates** with one line on why it didn't fit. When the contract expires or the ground shifts under it, surface a contract-refresh decision; do not keep sailing on a stale contract.

## Execute (free middle)

Do what the epic needs. Two hard requirements only:

1. **The ADMIRAL_LOG is the run's audit trail** (`templates/ADMIRAL_LOG.template.md`): every ruling, incident, merge, wave launch, and error you own goes in as it happens. With no gates in this step, the log is the accountability surface and the lessons audit's primary input. An unlogged ruling didn't happen.
2. **The latitude contract is honored**: adjudicate inside delegated classes (logged as RULING), escalate everything else.

Operating doctrine, learned from field fleets:

- One Commander per issue, each in an isolated worktree; pick model tier per issue complexity. Never two commanders in one worktree — stop/confirm-dead the original before launching a continuation into its worktree.
- Every dispatch carries a completed `templates/LAUNCH_ORDER.template.md`. Paste prior-wave verdict text — pointers are weak, commanders start cold. Pre-rule foreseeable ambiguities (marked overridable). A measured negative is a complete, successful deliverable: say so.
- One writer per shared document per wave; assign findings files explicitly.
- Status to the user per the contract: default stop-and-present at wave checkpoints; run ahead only when cleared.
- Merge green, reviewed PRs sequentially; **gate merges on check exit codes, never chain** a merge after a watch command. Verify main before each wave dispatch. Hold rebases to wave boundaries; if ground shifts under a running Commander, stop-and-relaunch on fresh ground rather than steering mid-flight.
- A Commander that dies or stalls: inspect its worktree (commits, workbench state, orphan processes) before acting; relaunch a continuation into the same worktree resuming from its engine state — don't restart from zero. Log every incident and recovery.
- **Surviving long detached compute is platform doctrine, not project lore** — the three kill vectors, watcher-sleep, the "completed"-but-sleeping hazard, detach + state-note-first, and the recovery drill live in `references/fleet-doctrine.md`. Carry its launch-execution rules into every launch order and follow its recovery drill when a ship dies; keep `.agent-work/LESSONS.md` for genuinely project-specific fleet rules rather than relearning the platform doctrine there.
- The project's playbook (`.agent-work/LESSONS.md` Active section) and platform invariants ride in every launch order's inherited-context block.

## Closeout (second bookend — the improvement engine)

The run cannot close with unrouted observations. Engine-enforced:

1. Dispatch a fresh-context subagent invoking `constellation-lessons-auditor` with a compiled run brief; every returned candidate gets a routed disposition (template delta / playbook delta / Charter nomination / constellation export / retire / drop-with-reason). Apply playbook deltas only via `apply_lessons_delta.py`.
2. Append the epic retrospective to `.agent-work/AGENT_FEEDBACK.md`; the feedback invariant check must pass.
3. Architecture audit: hand the epic's net change to `constellation-cartographer` for reconcile.
4. Repo hygiene: branches merged or dispositioned, worktrees swept, ADMIRAL_LOG archived to main under `.agent-work/archive/`.
5. Present the epic summary; user acceptance closes the run.

Templates: `templates/ADMIRAL_SPINE.template.json`, `templates/LATITUDE_CONTRACT.template.md`, `templates/LAUNCH_ORDER.template.md`, `templates/ADMIRAL_LOG.template.md`. References: `references/fleet-doctrine.md` (platform/harness survival doctrine). Engine: workbench `references/checklist-engine.md`.

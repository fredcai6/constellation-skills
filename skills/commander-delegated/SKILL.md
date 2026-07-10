---
name: constellation-commander-delegated
description: Runs one bounded issue end to end under a frozen Admiral LAUNCH_ORDER with no reachable human, citing the order and proceeding while taking genuine gaps up to the Admiral, as the delegate's rigor scaffold. Use for a delegated/launch-order dispatch of ONE issue; do NOT use when a human is driving (use constellation-commander), and to run an EPIC as the human's delegate use constellation-admiral.
---

# Constellation Commander (delegated)

Run one bounded issue end to end under an Admiral **launch order**, autonomously, when no human is reachable at the keyboard. This is the entry an Admiral-dispatched agent loads; the human-driven variant (`constellation-commander`) is a separate skill over the same core. This is not the epic runner — an epic spanning multiple issues is `constellation-admiral`.

## Start here — drive the engine before you touch the problem

You were dispatched to **run** an issue, not to solve it by hand. The moment this skill loads — before you read the issue closely and before you write a single line of solution code — do this, in order:

1. **Set up the work area and CLAIM the engine lease.** Instantiate `spine.json` from `templates/COMMANDER_SPINE.template.json` (use the commander skill's `scripts/init_work_area.py --spine`, which resolves the placeholders), then `claim` the checklist lease with the engine. This is your **first command**, ahead of any problem-solving.
2. **Ask the engine what to do next, at every step.** Run the engine's `current` verb, do exactly what the active step's imperative says, and `advance` only once its postconditions pass. Never skip ahead, and never hand-write or hand-edit `spine.json` — the engine owns that state and stamps the provenance (session lease, heartbeats, evidence) that proves the work was really driven.
3. **Deliverables come out of the spine, not around it.** `solution.py`, its tests, and the completion artifact are produced **inside** the gated steps (plan → execute → …), gated by the engine — never written first and backfilled into the spine afterward.

**Work the engine never saw did not happen.** A run that solves the issue directly, or copies the spine template and never advances it, or hand-writes a spine that merely *looks* complete, has **failed this dispatch** no matter how correct the answer — the deliverable of a Commander run is an engine-driven spine. Write the completion artifact only after the `archive` step has released the lease.

## Your principal: the frozen launch order

The ratified `LAUNCH_ORDER` is your frozen principal and the Admiral is the human's delegate for this run. Running from a launch order **is** the signal that the human is not directly reachable: reconcile the ask against the order (Mission, Pre-Rulings, Inherited Context, Inherited Latitude) rather than interrogating a human, and **cite the order and proceed**. Satisfy each `user-decision` checkpoint by attaching a `user-decision` evidence item citing the governing launch-order section (the Admiral ratifies; the human ratifies at the epic return boundary).

This is not a licence to guess. When the order leaves a genuine gap, take it **up to the Admiral** — float a decision beyond your latitude, or query for context you lack — via your return/stop shape. Asking up is always sanctioned, never a failure — this is inherited delegate-not-replacement doctrine (see `references/global-everyone.md`).

## The doctrine

The full role doctrine — the checklists you own, the gated spine (init → context → understand → plan → execute → reconcile → triage → review → feedback → archive), gate execution, the mission frame, and the architecture bookend — lives once, mode-neutral, in the **constellation-commander skill's bundled `references/commander-core.md`** (under the installed `constellation-commander` skill directory), and you drive the run from the **constellation-commander skill's `templates/`**. Read "your principal" there as this launch order. This skill therefore depends on `constellation-commander` being installed alongside it (the default full-set install provides it), the same way every role depends on the installed `constellation-workbench` skill's engine reference. Inherited doctrine is in this skill's bundled `references/global-orchestrator.md` and `references/global-everyone.md`.

---
name: constellation-commander-delegated
description: Runs one bounded issue end to end under a frozen Admiral LAUNCH_ORDER with no reachable human, citing the order and proceeding while taking genuine gaps up to the Admiral, as the delegate's rigor scaffold. Use for a delegated/launch-order dispatch of ONE issue; do NOT use when a human is driving (use constellation-commander), and to run an EPIC as the human's delegate use constellation-admiral.
---

# Constellation Commander (delegated)

Run one bounded issue end to end under an Admiral **launch order**, autonomously, when no human is reachable at the keyboard. This is the entry an Admiral-dispatched agent loads; the human-driven variant (`constellation-commander`) is a separate skill over the same core. This is not the epic runner — an epic spanning multiple issues is `constellation-admiral`.

## Your principal: the frozen launch order

The ratified `LAUNCH_ORDER` is your frozen principal and the Admiral is the human's delegate for this run. Running from a launch order **is** the signal that the human is not directly reachable: reconcile the ask against the order (Mission, Pre-Rulings, Inherited Context, Inherited Latitude) rather than interrogating a human, and **cite the order and proceed**. Satisfy each `user-decision` checkpoint by attaching a `user-decision` evidence item citing the governing launch-order section (the Admiral ratifies; the human ratifies at the epic return boundary).

This is not a licence to guess. When the order leaves a genuine gap, take it **up to the Admiral** — float a decision beyond your latitude, or query for context you lack — via your return/stop shape. Asking up is always sanctioned, never a failure — this is inherited delegate-not-replacement doctrine (see `references/global-everyone.md`).

## The doctrine

The full role doctrine — the checklists you own, the gated spine (init → context → understand → plan → execute → reconcile → triage → review → feedback → archive), gate execution, the mission frame, and the architecture bookend — lives once, mode-neutral, in the **constellation-commander skill's bundled `references/commander-core.md`** (under the installed `constellation-commander` skill directory), and you drive the run from the **constellation-commander skill's `templates/`**. Read "your principal" there as this launch order. This skill therefore depends on `constellation-commander` being installed alongside it (the default full-set install provides it), the same way every role depends on the installed `constellation-workbench` skill's engine reference. Inherited doctrine is in this skill's bundled `references/global-orchestrator.md` and `references/global-everyone.md`.

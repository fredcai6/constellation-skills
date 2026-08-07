# Prepped panel — Refresh / reach-up handoff (design-it-twice, 2 candidates, launch after gauge converges)

Interface under design: **module 4, Refresh** — how a near-full agent (soft-accepted or hard-forced) packages a handoff and signals its INVOKER to re-instantiate it fresh. Reach-up is settled (X3): Commander refreshes implementer/reviewer, Admiral refreshes Commander, human at top; self-refresh is a pi-only later seam. So the OPEN part is packaging + signal, NOT who does it.

Key facts to hand the designers:
- X1: cold-start is mostly free from existing engine state; the handoff should REFERENCE the spine/execute state + `why_trail` (Pocock don't-duplicate), not re-serialize them. `LAUNCH_ORDER.md` is already "governor-shaped" ("paste, don't point") but authored once at dispatch, not at a mid-run seam.
- Module 1 (approved): the `why_trail` + latest-`now_understand` digest already exist; Refresh reads `digest()`/`trail()`.
- Symmetric recovery: the same handoff shape must serve intentional refresh AND crash recovery.

Only 2 candidates (reach-up is settled, so less design space — surfaced count to human), distinct constraints:

- **Refresh-A · common-caller-first (reuse existing machinery)** — shape the handoff + signal to reuse what constellation already has: `LAUNCH_ORDER`-shaped payload, the crew-dispatch/`run_crew` registry, the existing STATE_NOTE. The "refresh request" is a normal agent return carrying a marker the invoker already knows how to consume + re-dispatch. Minimize NEW protocol. Honest cost: does bending to existing shapes lose anything the voluntary-seam case needs?
- **Refresh-B · minimal-interface (smallest new protocol)** — the smallest possible NEW handoff artifact + signal: a pointer-set (spine path + latest `why_trail` seq + current gate/seam) and a one-field "refresh requested" signal the invoker reads. Nothing re-serialized. Honest cost: is "smallest" under-specified for a cold-starting fresh agent, or exactly enough given the engine state already carries the rest?

Compared on: depth, locality, seam placement, testability. Each writes to `dit-refresh-{A-caller,B-minimal}.md`, returns 4-5 line summary. Design only. Model sonnet, background, watchdog on the pair.

Read list for both: `excursion-x1-result.md`, `DESIGN_SPEC.md` (modules 1 + 4), `LAUNCH_ORDER.template.md` + `STATE_NOTE.template.md` in the admiral/commander skills, `run_crew.py` docstring.

# Excursion X1 handoff — research (codebase, read-only)

## The one named question
For a fresh/resumed constellation agent at each tier (implementer, reviewer, commander, admiral), how much of a cold-start "resume block" is ALREADY provided by durable engine + handoff state today, and what is MISSING that a context-governor handoff would still have to supply?

## Task
Read-only inventory over the `constellation-skills` repo (`C:/Programs/constellation-skills`) and the installed skills at `C:/Users/fredc/.claude/skills/`. Examine the durable artifacts a resumed/fresh agent would rely on:
- `*_HANDOFF.template.md` (IMPLEMENTER, REVIEWER, CRITIC, PROTOTYPE), `ADMIRAL_LOG`, `WORKFLOW_CLOSEOUT`
- the checklist engine spine/state model (`checklist_engine.py`, `references/checklist-engine.md`, any `*SPINE*.template.json`)
- the "crash-resume state note" doctrine (grep `crash-resume`, `resume`, `reopen` in `references/global-everyone.md` and commander/admiral references)
- IDEAS_BOARD / source-of-truth conventions

## What "answered" looks like (the deliverable)
A per-tier inventory table: for each tier (implementer, reviewer, commander, admiral) —
- what a resumed agent RECONSTRUCTS today, and from which artifact;
- what it does NOT reconstruct (the gap a governor handoff would owe);
- your verdict: is the governor **THIN** (existing engine/handoff state ≈ sufficient for a clean refresh) or **RICH** (substantial new per-tier payload owed)?
End with an overall THIN/RICH/MIXED verdict and the SCOPE: what you examined and what you did NOT.

## Scope / stop conditions
- Read-only. Touch nothing. constellation-skills repo + installed skills only.
- ~1 focused pass; report even if inconclusive.
- Do NOT design the governor or propose mechanism — inventory the current state only.
- Scoped nulls: if a tier can't be assessed, say which and why; a null kills that assessment, not the question.

## Return format
Write your findings to `.agent-work/explore-context-governor/excursion-x1-result.md` (absolute: `C:/Programs/constellation-skills/.agent-work/explore-context-governor/excursion-x1-result.md`). Also return a short summary as your final message.

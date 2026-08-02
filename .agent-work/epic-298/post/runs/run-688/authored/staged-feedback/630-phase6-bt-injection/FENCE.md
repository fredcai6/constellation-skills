# Fence citation — 630-phase6-bt-injection

`durable_root()` resolved to this worktree (`C:/Programs/f1-phase6`), not the main checkout
(`C:/Programs/f1Brainz`), because an active Admiral epic-lease `spine.json`
(`status: active`, `claimed_by: admiral`) exists under the main checkout's `.agent-work/`
right now — concurrent sibling phase-commanders are running under the same epic #601 this
session (per the team roster: ShipA-623 through ShipJ-629 and others alongside this
Commander, Phase6Cmdr). Per `agent_work_root.py`'s documented fencing exception, the main
checkout is therefore fenced read-only for this run's durable-log write.

Governing launch order: `C:/Programs/f1Brainz/.agent-work/epic-601/wave10-630-launch-order.md`
(the Admiral's frozen launch order for this Commander dispatch). Per
`constellation-commander-delegated`'s own skill body: "Fenced feedback/archive closeout —
stage, do not waive... stage the worktree-local trio — the AGENT_FEEDBACK.md entry,
lessons-delta.json, and CONSTELLATION_FEEDBACK.md exports — plus a FENCE.md citing this
launch order, all under `.agent-work/staged-feedback/<work-id>/`... the Admiral harvests
that trio into the shared root at closeout."

Staged trio, all present under this directory (`.agent-work/staged-feedback/630-phase6-bt-injection/`):
- `AGENT_FEEDBACK.md` — the dated run entry, ready to append verbatim to the durable
  `<main>/.agent-work/AGENT_FEEDBACK.md`.
- `lessons-delta.json` — 5 ops (3 `confirm`, 2 `export` — the two `export` ops were chosen
  over a bare `confirm` because a dry-run against the worktree-local `LESSONS.md` copy
  flagged the two constellation-scope lessons as already at high recurrence-debt, 16 and 11
  prior confirmations respectively; exporting with a concrete upstream-fix proposal was
  judged more useful than a 17th/12th bare confirm), `tick: true`. Dry-run validated clean
  against this worktree's `LESSONS.md` copy (not applied — the Admiral applies against the
  durable copy at harvest).
- `CONSTELLATION_FEEDBACK.md` — the two export entries the delta above references.

Nothing in this staged trio was applied to any durable/shared file this run — only staged
here, per the fencing discipline. The worktree's own local `.agent-work/LESSONS.md` and
`.agent-work/AGENT_FEEDBACK.md` copies were read (for context/dry-run validation) but never
written.

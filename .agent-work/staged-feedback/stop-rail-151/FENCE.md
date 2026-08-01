# Fence citation — stop-rail-151

This run is fenced off the durable main-checkout `.agent-work/` root and may NOT
write it. The feedback/lessons closeout is therefore STAGED here (the trio +
this citation) for the Admiral to harvest into the shared root before sweeping
this worktree.

## Governing authority
- Launch order: `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/launch-orders/W2-151-stop-rail.md`
  - **Return Shape:** "workflow feedback (stage the fenced trio per doctrine and name its path — the durable root is the read-only main checkout)".
  - **Workspace:** all edits/commits from the worktree `C:/Programs/cs-wt-rail` only; "PR integration = server-side merge (Admiral merges)."
- Delegated Commander doctrine ("Fenced feedback/archive closeout — stage, do not waive"): stage the AGENT_FEEDBACK entry, lessons-delta.json, and CONSTELLATION_FEEDBACK exports under `.agent-work/staged-feedback/<work-id>/`, which `verify_agent_feedback.py` accepts in lieu of the durable-root write.

## Staged trio (present in this directory)
- `AGENT_FEEDBACK.md` — the run retrospective entry for stop-rail-151.
- `lessons-delta.json` — tick=true + one banked project lesson (harness-field / production-shaped-test discipline).
- `CONSTELLATION_FEEDBACK.md` — reasoned "no constellation exports this run".

Harvest target (Admiral, in main checkout): append the AGENT_FEEDBACK entry to
`.agent-work/AGENT_FEEDBACK.md`; apply lessons-delta.json via
`apply_lessons_delta.py --file .agent-work/LESSONS.md`.

# Crash-resume state note — 567-e

- **step:** outer spine `execute` (pending, not yet started — refresh-request e-execute-1
  attached against why-record w-4); inner `execute.json` (`.agent-work/567-e/execute.json`)
  not yet bound/claimed; nothing dispatched yet.
- **slug:** 567-e, branch `feat/567-e-door-rejection-episodes`, worktree
  `/home/tommy/projects/constellation-skills/.worktrees/567-e-door-rejection-episodes`
- **next command:** no detached process running. A fresh agent should: reload
  constellation-commander-delegated, call `spine_status` (reads DIGEST + REFRESH REQUESTED
  for `execute`), `start execute`, write/refresh this note again with the real next command
  once a crew dispatch begins, then drive `.agent-work/567-e/execute.json` per
  commander-core.md's "Executing a gate" — bind to it via `spine_bind` (release this outer
  lease first, spine_bind to the absolute path of execute.json, claim, drive g1-implement/
  review/integrate using `scripts/run_crew.py`, release, `spine_bind` back to
  `.agent-work/567-e/spine.json`, re-claim, then advance the outer `execute` step).
- **pid:** none — foreground, nothing detached yet.
- **expected artifact:** `.agent-work/epic-567-door/results/lane-e-RETURN.md` (final);
  intermediate: `.agent-work/567-e/execute.json` gates reaching `complete`, then
  `.agent-work/567-e/REPLAN_INPUT.json`.

**Design context for the successor, so it does not re-derive:** read
`.agent-work/567-e/notes-1.md`, `MISSION_FRAME.md`, and `DESIGN_NOTE.md` in that order before
touching `scripts/mcp_spine_server.py`. `DESIGN_NOTE.md`'s "Candidate A (corrected)" is the
frozen design g1-implement's handoff should follow verbatim; do not redesign from scratch.
One open item to float to the Admiral, not yet resolved: `docs/EPISODE_STORE.md` §10's
categorical "nothing should auto-create an episode" is in real tension with the launch
order's own acceptance criterion. Named, not decided — see DESIGN_NOTE.md's closing
paragraph and `execute.json`'s `capture-is-literal-derivation-only` decision anchor
(graded `guess`).

_Updated: 2026-08-17 (see spine_status heartbeat for exact time — this process does not
have wall-clock access)._

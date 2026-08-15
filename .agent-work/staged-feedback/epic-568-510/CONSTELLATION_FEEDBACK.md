# Workflow feedback export — epic-568-510 (wave-2 engine)

Staged for the Admiral to harvest: this run is FENCED from writing the durable root.

## Crew workflow feedback (harvested from the g2-engine falsifier)

- The handoff cited 'the Admiral's frozen launch order' without a path, and the launch order
  physically present in the worktree is the WAVE-1 one, whose settled/human pre-rulings forbid
  exactly this change. A reviewer trusting the in-worktree artifact would have blocked the change
  as a scope violation. Name the governing order by absolute path in every crew handoff.
- The handoff called one test 'deliberately failing' but did not state that the lane's baseline was
  therefore 1-red, so the reviewer could not distinguish a real regression from the known one until
  it re-ran the base commit itself. State baseline suite counts in the handoff.
- The reviewer declined the handoff's prescribed `git stash` for the red/green and used copy-aside +
  `git checkout HEAD -- <file>` + restore, because a stash in a worktree also holding live
  .agent-work/ state is recoverable only by hand if anything fails midway. It verified the restore
  by re-diffing to the exact pre-experiment diffstat.
- `record --finding` text goes through a shell, and unescaped backticks in findings were silently
  eaten by command substitution: two engine-recorded findings each lost a code-span literal.

## Commander reflection

Followed the frozen order closely, with three disclosed departures:
1. I corrected the order's stated premise rather than implementing it literally (the obedient start
   was never refused; the branding was the defect). Reported rather than worked around silently.
2. The harness refused the mandated FINDINGS file write; content folded into ENGINE_RESULT.md.
3. I drove closeout over the engine's hard line via the documented release path, with the reason
   recorded in each refresh-request's note field.

## Episodes recorded this run

- `epic-568-510-003` — Execute a human ruling that the engine must permit the `start` its HARD advisory instructs.
- `epic-568-510-004` — Change the smallest engine behavior that stops the compliance ledger branding an agent for obeying the advisory.
- `epic-568-510-005` — Obey pre-ruling 3: enumerate every test asserting on the refusal or the trip ledger BEFORE changing behavior.
- `epic-568-510-006` — Get the engine change independently falsified before closing the lane.
- `epic-568-510-007` — Record the run's findings at the path the frozen launch order names.
- `epic-568-510-008` — Drive this run's own spine to closeout through the engine.
- `epic-568-510-009` — Add a wave-2 gate to the run's existing execute.json sub-checklist so the engine sees the new work.
- `epic-568-510-010` — Interact with this run's spine through the MCP door, as prior orders required.

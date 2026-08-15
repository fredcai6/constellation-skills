# Crash-resume state note — epic-568-441

- **step:** execute · gate g1-implement · implementer crew dispatching (attempt-2 of gate g1/implementer, via run_crew.py --backend cli, run in background/foreground-blocking to avoid harness timeout; commander waits actively via background-task notification, does not end its turn)
- **slug:** epic-568-441 · epic-568/441-binding-store · /home/tommy/projects/constellation-skills/.worktrees/epic-568-441
- **next command:** python scripts/recover_crews.py epic-568-441 ; if resumable: python scripts/run_crew.py --resume constellation/epic-568-441/g1/implementer/attempt-2 --root /home/tommy/projects/constellation-skills/.worktrees/epic-568-441 ; else check .agent-work/epic-568-441/crew-handoffs/g1-implementer-result.md for a fresh result and integrate it into execute.json's g1-implement task
- **pid:** see .agent-work/epic-568-441/crew-runs.json entry for constellation/epic-568-441/g1/implementer/attempt-2 (pid field) for the live PID
- **expected artifact:** .agent-work/epic-568-441/crew-handoffs/g1-implementer-result.md

_Updated: 2026-08-15T17:01:21+00:00_

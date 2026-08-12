# Crash-resume state note — epic-559/c3-lifecycle

- **step:** execute · gate g5-review (carried findings) -- the LAST gate. Commander ran all six not_yet_written cases directly: the three non-bool forms refuse by fault name, the three legitimate forms are unchanged. Suite 2932, sweep 23.
- **slug:** epic-559/c3-lifecycle · branch `epic-559/c3-lifecycle` · worktree `/home/tommy/projects/constellation-skills-wt/c3-lifecycle`
- **next command:** `python scripts/run_crew.py --work-id epic-559/c3-lifecycle --gate g5 --role reviewer --model sonnet --worktree /home/tommy/projects/constellation-skills-wt/c3-lifecycle --handoff .agent-work/epic-559/c3-lifecycle/crew-handoffs/g5-reviewer-handoff.md --result .agent-work/epic-559/c3-lifecycle/crew-handoffs/g5-reviewer-result.md --parent constellation/epic-559/c3-lifecycle/execute/commander/attempt-1 --root /home/tommy/projects/constellation-skills-wt/c3-lifecycle --backend cli`
- **pid:** none — foreground (run_crew.py blocks; the Commander polls the result artifact inside its own turn, never by ending the turn)
- **expected artifact:** `.agent-work/epic-559/c3-lifecycle/crew-handoffs/g5-reviewer-result.md`

_Updated: 2026-08-12T13:20:00+00:00_

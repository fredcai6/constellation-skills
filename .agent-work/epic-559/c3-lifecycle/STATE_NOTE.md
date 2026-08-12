# Crash-resume state note — epic-559/c3-lifecycle

- **step:** execute · gate g4-review (declared dispatch). g4-implement landed and self-committed; Commander directly confirmed a wrong parent exits 1 and a matching one exits 0. Suite 2920, sweep 23.
- **slug:** epic-559/c3-lifecycle · branch `epic-559/c3-lifecycle` · worktree `/home/tommy/projects/constellation-skills-wt/c3-lifecycle`
- **next command:** `python scripts/run_crew.py --work-id epic-559/c3-lifecycle --gate g4 --role reviewer --model sonnet --worktree /home/tommy/projects/constellation-skills-wt/c3-lifecycle --handoff .agent-work/epic-559/c3-lifecycle/crew-handoffs/g4-reviewer-handoff.md --result .agent-work/epic-559/c3-lifecycle/crew-handoffs/g4-reviewer-result.md --parent constellation/epic-559/c3-lifecycle/execute/commander/attempt-1 --root /home/tommy/projects/constellation-skills-wt/c3-lifecycle --backend cli`
- **pid:** none — foreground (run_crew.py blocks; the Commander polls the result artifact inside its own turn, never by ending the turn)
- **expected artifact:** `.agent-work/epic-559/c3-lifecycle/crew-handoffs/g4-reviewer-result.md`

_Updated: 2026-08-12T12:40:00+00:00_

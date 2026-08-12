# Crash-resume state note — epic-559/c2-generate-the-spine

- **step:** execute · gate g3-review (cold review of the dispatch proof)
- **slug:** `epic-559/c2-generate-the-spine`, branch `epic-559/c2-generate-the-spine`, worktree `/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine`
- **next command:** `python scripts/recover_crews.py epic-559/c2-generate-the-spine` then `python scripts/run_crew.py --work-id epic-559/c2-generate-the-spine --gate g3-review --role reviewer --model sonnet --worktree . --parent admiral-epic-418-followon --handoff .agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g3-review-handoff.md --result .agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g3-review-result.md`
- **pid:** filled at dispatch below; the commander itself is pid 1729161 (foreground). The g1 implementer is dispatched via run_crew.py in the background and polled inside the turn.
- **expected artifact:** `.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g3-review-result.md`. Final run artifact: `.agent-work/epic-559/c2-generate-the-spine/COMMANDER_RETURN.md`.

_Updated: 2026-08-11T16:40:00+00:00_

# Crash-resume state note — epic-559/c2-generate-the-spine

- **step:** execute · gate g2-review ROUND 2 (after rework)
- **slug:** `epic-559/c2-generate-the-spine`, branch `epic-559/c2-generate-the-spine`, worktree `/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine`
- **next command:** `python scripts/recover_crews.py epic-559/c2-generate-the-spine` — then, once g0-design's DESIGN_NOTE.md exists and the gate is advanced: `python scripts/run_crew.py --work-id epic-559/c2-generate-the-spine --gate g2-review --role reviewer --model sonnet --worktree . --parent admiral-epic-418-followon --handoff .agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g2-review-handoff.md --result .agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g2-review-result.md`
- **pid:** filled at dispatch below; the commander itself is pid 1729161 (foreground). The g1 implementer is dispatched via run_crew.py in the background and polled inside the turn.
- **expected artifact:** `.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g2-review-result.md` for the next dispatch. Final run artifact: `.agent-work/epic-559/c2-generate-the-spine/COMMANDER_RETURN.md`.

_Updated: 2026-08-11T16:40:00+00:00_

# Crash-resume state note — epic-178

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

- **step:** execute · Wave 1 dispatch (issues #182 Trip/AFK, #183 Refresh/HITL). Wave 0 (#179,#180,#181) DONE + merged to main e2b8005.
- **slug:** epic-178 · main checkout C:/Programs/constellation-skills (synced to origin/main e2b8005, now running the NEW #179 engine) · admiral spine .agent-work/epic-178/spine.json · session-id admiral-epic-178. Wave 1 worktrees: wt-182 (epic178-182-trip), wt-183 (epic178-183-refresh), both base e2b8005.
- **next command:** py scripts/checklist_engine.py --file .agent-work/epic-178/spine.json current  (then inspect .agent-work/epic-178/crew-handoffs/18{2,3}-result.md and the wt-182/wt-183 worktrees; reviewers run in wt-18X-rev detached worktrees)
- **pid:** none — foreground (Admiral drives in-context; implementers/reviewers are Agent-tool background subagents tracked by the harness, not OS-detached PIDs)
- **expected artifact:** Wave 1 result artifacts .agent-work/epic-178/crew-handoffs/18{2,3}-result.md; merged PR for #182; #183 built to the HITL qualitative-sign-off seam. NOTE: remaining spine advances (execute→closeout) run on the NEW engine and require --why. HITL held for human: #180 settings.json wiring; #183 symmetric-recovery sign-off.

_Updated: 2026-07-18T01:05:00Z_

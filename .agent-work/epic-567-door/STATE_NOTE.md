# Crash-resume state note — epic-567-door

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

- **step:** execute · **wave 1 merged and verified; handed off for a session cycle.** Admiral spine `.agent-work/epic-567-door/spine.json`, step `execute`, status in-progress, **lease deliberately released** so the next session claims cleanly instead of forcing. Wave 2 (lanes D/E/F) not started and needs a fresh latitude contract.
- **slug:** epic-567-door · main checkout `/home/tommy/projects/constellation-skills` · `origin/main` @ `178cb9ec` (3352 passed / 0 failed on Linux) · lane branches `feat/567-{a,b,c,g}-*` all merged and **kept** (#412) · all four lane worktrees swept
- **next command:** read `.agent-work/HANDOFF-2026-08-17-epic-567-wave-2.md` first, then `mcp__spine__spine_bind(spine_file="/home/tommy/projects/constellation-skills/.agent-work/epic-567-door/spine.json")` — a fresh session's door has that verb, this one's did not — then claim the lease: `py /home/tommy/.claude/skills/constellation-admiral/scripts/checklist_engine.py --file .agent-work/epic-567-door/spine.json claim --session-id <yours> --claimed-by admiral --worktree .`
- **pid:** none — foreground; no OS-detached process, and every wave-1 Commander is finished and confirmed gone
- **expected artifact:** for wave 2, a fresh `LATITUDE_CONTRACT` confirmation plus `transitions/w2/` packets; for closeout, `episodes/` entries for this epic plus the ADMIRAL_LOG archived under `.agent-work/archive/`

_Updated: 2026-08-17T16:40:00Z — handoff written for a session cycle. Wave 1 complete: PRs #623, #621, #620, #622 merged, plus #626 (q4's subtest guard). Tommy ruled q1–q4; the net-deletion pre-ruling is withdrawn and the merge gate is Linux-green-in-a-clean-worktree. 24 triage candidates staged, none filed. `main` was broken mid-run by another session's #624 and repaired by its #625 — re-check `git rev-parse origin/main` before starting, because main moved under this Admiral twice._

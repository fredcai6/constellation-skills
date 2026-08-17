# Crash-resume state note — epic-567-door

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

- **step:** execute · wave 1 **merged and verified**; now harvesting and sweeping the four lane worktrees, then awaiting the human's call on wave 2 versus closeout. Admiral spine `.agent-work/epic-567-door/spine.json`, step `execute`, status in-progress.
- **slug:** epic-567-door · main checkout `/home/tommy/projects/constellation-skills` on `main` @ `d437ab63` (post-merge, suite green on Linux 3344/0) · lane branches `feat/567-{a,b,c,g}-*` all merged and **kept** (#412 — do not delete) · worktrees `.worktrees/567-{a,b,c,g}-*` pending sweep
- **next command:** `py /home/tommy/.claude/skills/constellation-admiral/scripts/checklist_engine.py --file .agent-work/epic-567-door/spine.json current --session-id a4704163-34f0-4c9f-aca6-8d68c189ab36`
- **pid:** none — foreground (no OS-detached process; all Commanders are finished in-process subagents)
- **expected artifact:** `.agent-work/epic-567-door/harvest/` holding each lane's feedback export, then the four worktrees gone from `git worktree list`

_Updated: 2026-08-17T15:10:00Z — wave 1 is on main. Four merges: #623→4573ef17, #621→6668b7ff, #620→9e1185af, #622→22f9637d, then d437ab63 regenerated the code map and relocated the lane returns out of the repo root. Human ruled q1–q3; q4 (scope of the subTest-reads-PASSED finding, 169 call sites across 25 files) is still open and does not block harvest or sweep. Wave 2 (lanes D/E/F) has not run and needs a fresh latitude contract — this one expired at the W1 checkpoint._

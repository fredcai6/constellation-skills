# Crash-resume state note — 20260706-dogfood-audit

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

The engine enforces the floor: the spine `execute` step has a `command`
precondition (`verify_state_note.py`) that refuses to enter the detach-heavy
phase until every field below is filled. Keeping it current across detaches is
your discipline; the engine only guarantees the first one exists.

- **step:** execute · waves 1+2 in flight. Done: #42 (PR #57 MERGED, main e4c922d). Running: wave1-44/46/49/56 (bases 363d27a), wave2-43/45/50/51 (bases e4c922d). Queued: #47 on #44 merge (engine seat); wave 3 = #48/#52/#53/#54/#55; wave 4 (user scope add) = #58/#59/#60/#61. HITL ratifications due at wave-2/3 checkpoints.
- **slug:** 20260706-dogfood-audit · main checkout on constellation/lessons-apply-or-defer (merged; safe to leave) · C:/Programs/constellation-skills · worktrees under C:/Programs/constellation-skills-worktrees/issue-NN
- **next command:** python C:/Programs/constellation-skills/scripts/checklist_engine.py --file .agent-work/20260706-dogfood-audit/spine.json current  (then read ADMIRAL_LOG.md + LATITUDE_CONTRACT.md PR-2; collect commander verdicts from .agent-work/issue-NN/VERDICT.md in each worktree; merge green+reviewed PRs sequentially; append AGENT_FEEDBACK entries from verdicts to .agent-work/AGENT_FEEDBACK.md)
- **pid:** none — foreground (commanders are harness background agents: wave1-44, wave1-46, wave1-49, wave1-56, wave2-43, wave2-45, wave2-50, wave2-51)
- **expected artifact:** .agent-work/20260706-dogfood-audit/evidence/wave1-verdicts.md + wave2-verdicts.md (verdicts pasted as they land); VERDICT.md per worktree

_Updated: 2026-07-06T21:20:00-07:00_

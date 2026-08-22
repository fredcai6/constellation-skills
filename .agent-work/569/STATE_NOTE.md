# Crash-resume state note — 569

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

- **step:** execute · wave 1 DISPATCHED and in flight (two commanders running); Admiral is waiting to adjudicate, not working
- **slug:** work-id `569`, Admiral spine `.agent-work/569/spine.json` (session `constellation/569`, lease active) driven from the main checkout /home/tommy/projects/constellation-skills on `main` @ 7aa835a2. Commanders: `w1-wiring` in /home/tommy/projects/569-w1-wiring (branch epic-569/w1-wiring, spine .agent-work/w1-wiring/spine.json, session constellation/w1-wiring); `w1-verdict` in /home/tommy/projects/569-w1-verdict (branch epic-569/w1-verdict, spine .agent-work/w1-verdict/spine.json, session constellation/w1-verdict). Both based on 244665ee.
- **next command:** check both commanders for completion — `ls /home/tommy/projects/569-w1-wiring/.agent-work/w1-wiring/RESULT.md /home/tommy/projects/569-w1-verdict/.agent-work/w1-verdict/RESULT.md`. If present, adjudicate and merge per .agent-work/569/LATITUDE_CONTRACT.md; then author the wave-1→wave-2 transition under .agent-work/569/transitions/w1-to-w2/ and run `python3 /home/tommy/.claude/skills/constellation-admiral/scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id 569` before dispatching wave 2 (#556/#557). If a commander is dead, inspect its worktree and relaunch a continuation into the SAME worktree and spine — never restart from zero.
- **pid:** none — foreground; commanders are in-harness Agent-tool subagents, not OS processes. A background Monitor (task brulx8emm) polls both worktrees for commits, RESULT.md, and spine progress.
- **expected artifact:** .agent-work/w1-wiring/RESULT.md and .agent-work/w1-verdict/RESULT.md inside their respective worktrees, plus two merged PRs on main

**DO NOT** claim a lease on `constellation/w1-wiring` or `constellation/w1-verdict`. Those are the
commanders' own spines. The Stop hook has already misreported one of them as the Admiral's abandoned
run; see the INCIDENT entry in ADMIRAL_LOG.md. The Admiral's spine is `constellation/569` and nothing
else.

_Updated: 2026-08-22T14:50:00+00:00_

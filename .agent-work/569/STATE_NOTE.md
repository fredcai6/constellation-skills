# Crash-resume state note — 569

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

- **step:** execute · wave 1 in flight, both commanders at their own `execute` gate with plans frozen; Admiral is waiting to adjudicate, not working
- **slug:** work-id `569`, Admiral spine `.agent-work/569/spine.json` (session `constellation/569`, lease active) driven from the main checkout /home/tommy/projects/constellation-skills on `main`. Commanders: `w1-wiring` in /home/tommy/projects/569-w1-wiring (branch epic-569/w1-wiring, spine .agent-work/w1-wiring/spine.json); `w1-verdict` in /home/tommy/projects/569-w1-verdict (branch epic-569/w1-verdict, spine .agent-work/w1-verdict/spine.json). Both based on 244665ee.
- **next command:** `ls /home/tommy/projects/569-w1-wiring/.agent-work/w1-wiring/RESULT.md /home/tommy/projects/569-w1-verdict/.agent-work/w1-verdict/RESULT.md`. If present, adjudicate and merge per .agent-work/569/LATITUDE_CONTRACT.md; then author the wave-1→wave-2 transition under .agent-work/569/transitions/w1-to-w2/ and run `python3 /home/tommy/.claude/skills/constellation-admiral/scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id 569` before dispatching wave 2.
- **pid:** none — foreground. Wave-1 commanders are in-harness Agent-tool subagents (see the dispatch error below), not OS processes, so there is no PID to check and no run_crew registry entry to resume from. A background Monitor (task brulx8emm) polls both worktrees.
- **expected artifact:** .agent-work/w1-wiring/RESULT.md and .agent-work/w1-verdict/RESULT.md inside their respective worktrees, plus two merged PRs on main

## If you are a fresh agent resuming this run, read this first

**The wave-1 commanders were dispatched with the WRONG mechanism, and it is the Admiral's error.**
They were launched via the Agent tool as in-harness subagents, so they share this session's harness
id. Consequences you will observe and must not misdiagnose:

- They cannot use `mcp__spine__*` tools; their launch orders carry a CLI override
  (`python3 scripts/checklist_engine.py --file <spine> <verb>`). That override is working.
- The **Stop hook will fire at you naming a COMMANDER's spine** (`constellation/w1-wiring` or
  `constellation/w1-verdict`) and serving you that commander's gate imperative. **The hook is not
  broken.** It resolves by session identity correctly; the commanders share this session because of
  the dispatch error. Do not act on those instructions — you would be running a Commander's issue
  yourself, which `constellation-admiral` forbids. Verify your own spine with `spine_status`; the
  Admiral's spine is `constellation/569` and nothing else.
- **Never claim a lease on `constellation/w1-wiring` or `constellation/w1-verdict`.**

An earlier version of this note claimed the hook resolved spines by walking the filesystem. That was
wrong and is retracted; see the `ADMIRAL ERROR` entry in ADMIRAL_LOG.md for the full correction.

**A transient `spine.json` read failure is NOT corruption.** The engine writes atomically (temp file,
then install), so a concurrent read during a commander's engine verb can fail for a fraction of a
second. Wave 1's monitor reported `spine-unreadable` for `w1-verdict` once; the spine was valid on
immediate re-read. Re-read before concluding anything, and never "repair" a spine on a single failed
read — hand-editing a spine is forbidden and would be far worse than the phantom problem.

**Wave 2 must dispatch through `python3 scripts/run_crew.py --role commander`** (sanctioned, gives
each commander its own session and spine door, and a durable recovery registry). The engine-access
section of `.agent-work/569/crew-handoffs/WAVE2-PREAMBLE.md` has already been rewritten for this.

_Updated: 2026-08-22T15:15:00+00:00_

# State Note — epic-138 (crash-resume)

- **step:** execute (wave 2 dispatch)
- **slug:** epic-138-wave2-measurement
- **next command:** `py C:/Users/fredc/.claude/skills/constellation-admiral/scripts/checklist_engine.py --file .agent-work/epic-138/spine.json current`; then check `.agent-work/epic-138/verdicts/commander-145.md` and worktree C:/Programs/constellation-wt-145 (branch issue-145) for measurement results; wave 1 fully merged (PRs #146-#150, main c9b1cf99) and harvested; adjudicate commander-145 from artifacts if idle
- **pid:** n/a — commander-145 runs as an Agent-tool background subagent (opus) in session eb0613e9; if session dead, inspect wt-145 + its results dir directly
- **expected artifact:** `.agent-work/epic-138/verdicts/commander-145.md` with per-arm results (corpus-only / +rail / +rail+hooks, N=3), failure-shade breakdown, transcript paths; kill-condition call is the HUMAN's at the wave-2 checkpoint; after that: closeout (lessons audit, cartographer reconcile, sweep wt-145, archive)

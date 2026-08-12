#!/usr/bin/env bash
set -u
WT="/home/tommy/projects/constellation-skills-wt/c3-lifecycle"
AW="$WT/.agent-work/epic-559/c3-lifecycle"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py \
  --work-id "epic-559/c3-lifecycle" --gate execute --role commander \
  --model opus --parent "admiral-epic-418-followon" \
  --worktree "$WT" \
  --spine "$AW/execute.json" \
  --handoff "$AW/LAUNCH_ORDER.md" \
  --result "$AW/COMMANDER_RETURN.md" \
  --backend cli

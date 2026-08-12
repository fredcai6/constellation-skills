#!/usr/bin/env bash
set -u
WT="/home/tommy/projects/constellation-skills-wt/c3-lifecycle"
AW="$WT/.agent-work/epic-559/r0-lifecycle-repair"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py \
  --work-id "epic-559/r0-lifecycle-repair" --gate m1 --role implementer \
  --model sonnet --parent "admiral-epic-418-followon" \
  --worktree "$WT" \
  --spine "$AW/plan.json" \
  --handoff "$AW/LAUNCH_ORDER.md" \
  --result "$AW/IMPLEMENTER_RESULT.md" \
  --backend cli

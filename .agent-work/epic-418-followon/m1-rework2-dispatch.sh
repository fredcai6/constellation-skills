#!/usr/bin/env bash
set -u
WT=/home/tommy/projects/constellation-skills-wt/m1-door-binding
WORKID=epic-418-followon/m1-door-binding
D="$WT/.agent-work/$WORKID"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py \
  --work-id "$WORKID" --gate g5-rework2 --role implementer --model sonnet \
  --worktree "$WT" --spine "$D/REWORK2_PLAN.json" \
  --handoff "$D/REWORK2_HANDOFF.md" --result "$D/REWORK2_RESULT.md" --backend cli

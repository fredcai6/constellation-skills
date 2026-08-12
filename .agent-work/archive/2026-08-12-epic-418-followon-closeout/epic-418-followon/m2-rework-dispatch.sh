#!/usr/bin/env bash
set -u
WT=/home/tommy/projects/constellation-skills-wt/m2-mechanical
WORKID=epic-418-followon/m2-mechanical
D="$WT/.agent-work/$WORKID"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py --work-id "$WORKID" --gate g3-rework --role implementer --model sonnet \
  --worktree "$WT" --spine "$D/REWORK_PLAN.json" \
  --handoff "$D/REWORK_HANDOFF.md" --result "$D/REWORK_RESULT.md" --backend cli

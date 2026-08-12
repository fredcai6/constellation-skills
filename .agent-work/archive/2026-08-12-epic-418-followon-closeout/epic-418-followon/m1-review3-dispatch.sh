#!/usr/bin/env bash
set -u
WT=/home/tommy/projects/constellation-skills-wt/m1-door-binding
WORKID=epic-418-followon/m1-door-binding
D="$WT/.agent-work/$WORKID"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py \
  --work-id "$WORKID" --gate g6-review3 --role reviewer --model opus \
  --worktree "$WT" --spine "$D/REVIEW3_SURVEY.json" \
  --handoff "$D/REVIEWER3_HANDOFF.md" --result "$D/REVIEWER3_RESULT.md" --backend cli

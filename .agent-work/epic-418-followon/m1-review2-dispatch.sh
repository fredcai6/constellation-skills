#!/usr/bin/env bash
set -u
WT=/home/tommy/projects/constellation-skills-wt/m1-door-binding
WORKID=epic-418-followon/m1-door-binding
D="$WT/.agent-work/$WORKID"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py \
  --work-id "$WORKID" --gate g4-review2 --role reviewer --model opus \
  --worktree "$WT" --spine "$D/REVIEW2_SURVEY.json" \
  --handoff "$D/REVIEWER2_HANDOFF.md" --result "$D/REVIEWER2_RESULT.md" --backend cli

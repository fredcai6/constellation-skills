#!/usr/bin/env bash
set -u
WT=/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job
WORKID=epic-559/a-spine-is-the-job
D="$WT/.agent-work/$WORKID"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py --work-id "$WORKID" --gate w1-completion-contract --role implementer --model sonnet \
  --worktree "$WT" --spine "$D/REWORK_PLAN.json" \
  --handoff "$D/REWORK_HANDOFF.md" --result "$D/IMPLEMENTER_RESULT.md" --backend cli

#!/usr/bin/env bash
set -u
WT=/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks
WORKID=epic-559/b-instructions-to-checks
D="$WT/.agent-work/$WORKID"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py --work-id "$WORKID" --gate g1-implement --role implementer --model sonnet \
  --worktree "$WT" --spine "$D/IMPLEMENTER_PLAN.json" \
  --handoff "$D/HANDOFF.md" --result "$D/IMPLEMENTER_RESULT.md" --backend cli

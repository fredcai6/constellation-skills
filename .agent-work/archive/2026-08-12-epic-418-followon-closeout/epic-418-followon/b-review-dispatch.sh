#!/usr/bin/env bash
set -u
WT=/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks
WORKID=epic-559/b-instructions-to-checks
D="$WT/.agent-work/$WORKID"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py --work-id "$WORKID" --gate g2-review --role reviewer --model sonnet \
  --worktree "$WT" --spine "$D/REVIEW_SURVEY.json" \
  --handoff "$D/REVIEW_HANDOFF.md" --result "$D/REVIEWER_RESULT.md" --backend cli

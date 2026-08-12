#!/usr/bin/env bash
set -u
# No SPINE_FILE/SPINE_SESSION export: run_crew.py binds them (M1, merged).
WT=/home/tommy/projects/constellation-skills-wt/m2-mechanical
WORKID=epic-418-followon/m2-mechanical
D="$WT/.agent-work/$WORKID"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py --work-id "$WORKID" --gate g5-review --role reviewer --model sonnet \
  --worktree "$WT" --spine "$D/REVIEW_SURVEY.json" \
  --handoff "$D/REVIEW_HANDOFF.md" --result "$D/REVIEWER_RESULT.md" --backend cli

#!/usr/bin/env bash
# Cold review of M1. Deliberately exports NO SPINE_* — the new --spine flag must do the binding,
# which makes this dispatch an end-to-end test of the committed change itself.
set -u
WT=/home/tommy/projects/constellation-skills-wt/m1-door-binding
WORKID=epic-418-followon/m1-door-binding
D="$WT/.agent-work/$WORKID"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py \
  --work-id "$WORKID" \
  --gate g2-review \
  --role reviewer \
  --model opus \
  --worktree "$WT" \
  --spine "$D/REVIEW_SURVEY.json" \
  --handoff "$D/REVIEWER_HANDOFF.md" \
  --result "$D/REVIEWER_RESULT.md" \
  --backend cli

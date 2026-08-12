#!/usr/bin/env bash
set -u
# No SPINE_FILE/SPINE_SESSION export: run_crew.py binds them (M1, merged 27a5adf5).
WT=/home/tommy/projects/constellation-skills-wt/n1-verb-closure
WORKID=epic-418-followon/n1-verb-closure
D="$WT/.agent-work/$WORKID"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py --work-id "$WORKID" --gate g1-implement --role implementer --model sonnet \
  --worktree "$WT" --spine "$D/IMPLEMENTER_PLAN.json" \
  --handoff "$D/HANDOFF.md" --result "$D/IMPLEMENTER_RESULT.md" --backend cli

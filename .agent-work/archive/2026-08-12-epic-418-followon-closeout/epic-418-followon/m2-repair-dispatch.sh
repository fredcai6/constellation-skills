#!/usr/bin/env bash
set -u
# DELIBERATELY does not export SPINE_FILE / SPINE_SESSION.
# M1 merged, so scripts/run_crew.py binds them for every crew now. This dispatch
# is the production test of that. Adding the env here would destroy the measurement.
WT=/home/tommy/projects/constellation-skills-wt/m2-mechanical
WORKID=epic-418-followon/m2-mechanical
D="$WT/.agent-work/$WORKID"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py --work-id "$WORKID" --gate g4-repair --role implementer --model sonnet \
  --worktree "$WT" --spine "$D/REPAIR_PLAN.json" \
  --handoff "$D/REPAIR_HANDOFF.md" --result "$D/REPAIR_RESULT.md" --backend cli

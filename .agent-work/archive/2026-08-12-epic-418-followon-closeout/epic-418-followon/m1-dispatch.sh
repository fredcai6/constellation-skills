#!/usr/bin/env bash
# Dispatch M1. Re-runnable: recover_crews.py first, per the state note.
set -u
WT=/home/tommy/projects/constellation-skills-wt/m1-door-binding
WORKID=epic-418-followon/m1-door-binding
# The bootstrap this very change productionizes: bind the crew's door to ITS OWN spine,
# with the assignment-keyed identity (no attempt tail). crew_env() copies os.environ.
export SPINE_FILE="$WT/.agent-work/$WORKID/IMPLEMENTER_PLAN.json"
export SPINE_ENGINE="$WT/scripts/checklist_engine.py"
export SPINE_SESSION="constellation/$WORKID/g1-implement/implementer"
cd "$WT" || exit 1
exec python3 scripts/run_crew.py \
  --work-id "$WORKID" \
  --gate g1-implement \
  --role implementer \
  --model sonnet \
  --worktree "$WT" \
  --handoff "$WT/.agent-work/$WORKID/HANDOFF.md" \
  --result "$WT/.agent-work/$WORKID/IMPLEMENTER_RESULT.md" \
  --backend cli

#!/usr/bin/env bash
set -u
cd "/home/tommy/projects/constellation-skills-wt/d1-stale-pins" || exit 1
exec python3 scripts/run_crew.py --work-id "epic-559/d1-stale-pins" --gate h1-pins --role implementer --model sonnet \
  --worktree "/home/tommy/projects/constellation-skills-wt/d1-stale-pins" --spine "/home/tommy/projects/constellation-skills-wt/d1-stale-pins/.agent-work/epic-559/d1-stale-pins/IMPLEMENTER_PLAN.json" --handoff "/home/tommy/projects/constellation-skills-wt/d1-stale-pins/.agent-work/epic-559/d1-stale-pins/HANDOFF.md" \
  --result "/home/tommy/projects/constellation-skills-wt/d1-stale-pins/.agent-work/epic-559/d1-stale-pins/IMPLEMENTER_RESULT.md" --backend cli

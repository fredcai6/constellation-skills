#!/usr/bin/env bash
set -u
cd "/home/tommy/projects/constellation-skills-wt/c1-spine-lint" || exit 1
exec python3 scripts/run_crew.py --work-id "epic-559/c1-spine-lint" --gate g1-shape --role implementer --model sonnet \
  --worktree "/home/tommy/projects/constellation-skills-wt/c1-spine-lint" --spine "/home/tommy/projects/constellation-skills-wt/c1-spine-lint/.agent-work/epic-559/c1-spine-lint/IMPLEMENTER_PLAN.json" --handoff "/home/tommy/projects/constellation-skills-wt/c1-spine-lint/.agent-work/epic-559/c1-spine-lint/HANDOFF.md" \
  --result "/home/tommy/projects/constellation-skills-wt/c1-spine-lint/.agent-work/epic-559/c1-spine-lint/IMPLEMENTER_RESULT.md" --backend cli

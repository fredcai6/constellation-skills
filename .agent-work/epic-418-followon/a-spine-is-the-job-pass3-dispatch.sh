#!/usr/bin/env bash
set -u
cd "/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job" || exit 1
exec python3 scripts/run_crew.py --work-id "epic-559/a-spine-is-the-job" --gate x1-installed-bundle --role implementer --model sonnet \
  --worktree "/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job" --spine "/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job/.agent-work/epic-559/a-spine-is-the-job/REWORK2_PLAN.json" --handoff "/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job/.agent-work/epic-559/a-spine-is-the-job/REWORK2_HANDOFF.md" --result "/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job/.agent-work/epic-559/a-spine-is-the-job/IMPLEMENTER_RESULT.md" --backend cli

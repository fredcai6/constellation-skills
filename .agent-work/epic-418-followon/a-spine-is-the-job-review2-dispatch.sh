#!/usr/bin/env bash
set -u
cd "/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job" || exit 1
exec python3 scripts/run_crew.py --work-id "epic-559/a-spine-is-the-job" --gate g3-review2 --role reviewer --model opus \
  --worktree "/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job" --spine "/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job/.agent-work/epic-559/a-spine-is-the-job/REVIEW_SURVEY2.json" \
  --handoff "/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job/.agent-work/epic-559/a-spine-is-the-job/REVIEW_HANDOFF2.md" --result "/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job/.agent-work/epic-559/a-spine-is-the-job/REVIEWER_RESULT2.md" --backend cli

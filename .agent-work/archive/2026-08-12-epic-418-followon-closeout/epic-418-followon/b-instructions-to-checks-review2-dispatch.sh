#!/usr/bin/env bash
set -u
cd "/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks" || exit 1
exec python3 scripts/run_crew.py --work-id "epic-559/b-instructions-to-checks" --gate g3-review2 --role reviewer --model sonnet \
  --worktree "/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks" --spine "/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks/.agent-work/epic-559/b-instructions-to-checks/REVIEW_SURVEY2.json" \
  --handoff "/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks/.agent-work/epic-559/b-instructions-to-checks/REVIEW_HANDOFF2.md" --result "/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks/.agent-work/epic-559/b-instructions-to-checks/REVIEWER_RESULT2.md" --backend cli

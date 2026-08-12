#!/usr/bin/env bash
set -u
cd "/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks" || exit 1
exec python3 scripts/run_crew.py --work-id "epic-559/b-instructions-to-checks" --gate y1-map --role implementer --model sonnet \
  --worktree "/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks" --spine "/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks/.agent-work/epic-559/b-instructions-to-checks/FIX_PLAN.json" --handoff "/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks/.agent-work/epic-559/b-instructions-to-checks/FIX_HANDOFF.md" --result "/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks/.agent-work/epic-559/b-instructions-to-checks/IMPLEMENTER_RESULT.md" --backend cli

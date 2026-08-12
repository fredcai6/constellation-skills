#!/usr/bin/env bash
set -u
cd "/home/tommy/projects/constellation-skills-wt/e1-fail-up" || exit 1
exec python3 scripts/run_crew.py --work-id "epic-559/e1-fail-up" --gate f1-bind-parent --role implementer --model sonnet \
  --worktree "/home/tommy/projects/constellation-skills-wt/e1-fail-up" --spine "/home/tommy/projects/constellation-skills-wt/e1-fail-up/.agent-work/epic-559/e1-fail-up/IMPLEMENTER_PLAN.json" --handoff "/home/tommy/projects/constellation-skills-wt/e1-fail-up/.agent-work/epic-559/e1-fail-up/HANDOFF.md" \
  --result "/home/tommy/projects/constellation-skills-wt/e1-fail-up/.agent-work/epic-559/e1-fail-up/IMPLEMENTER_RESULT.md" --backend cli

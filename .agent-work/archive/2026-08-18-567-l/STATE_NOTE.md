# Crash-resume state note — 567-l

- **step:** execute · gate g1-implement (episode-observation guard rephrase)
- **slug:** 567-l, branch feat/567-j-launcher-declared-defaults, worktree /home/tommy/projects/constellation-skills/.worktrees/567-j-launcher-declared-defaults
- **next command:** run g1's imperative in execute.json: `python3 scripts/apply_episode_delta.py --delta <delta.json> --store-root episodes` restating 567-j-004.a5, then `python3 -m pytest tests/test_episode_observations.py::RealStoreTests -q`
- **pid:** none — foreground (all three gates run in-context, no detached process)
- **expected artifact:** episodes/active/567-j-004.md (a5 restated); scripts/run_crew.py (commander tier row); a new scripts/check_role_spine_bookends.py + tests/test_check_role_spine_bookends.py; finally .agent-work/epic-567-door/results/lane-l-RETURN.md

_Updated: 2026-08-18T06:42Z_

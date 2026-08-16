# Crash-resume state note — egaw-merge-main

- **step:** execute · gate g1-merge
- **slug:** egaw-merge-main, branch fix/episode-guard-at-write, worktree /home/tommy/projects/constellation-skills/.worktrees/episode-guard-at-write
- **next command:** git merge origin/main (expect ONLY map/INDEX.md to conflict; if so, `python -m scripts.code_map build --root .` then `git add map/INDEX.md && git commit`)
- **pid:** none — foreground
- **expected artifact:** a merge commit on fix/episode-guard-at-write with MERGE_HEAD cleared and tests/test_code_map.py green

_Updated: 2026-08-16T03:28:14Z_

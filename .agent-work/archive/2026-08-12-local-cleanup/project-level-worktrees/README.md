# Project-Level Worktree Sweep

Date: 2026-08-12

Preserved project-level Constellation residue before removing sibling directories:

- C:/Programs/constellation-skills-wt/s -> constellation-skills-wt-s/; small checklist context/mechanical files.
- C:/Programs/constellation-skills-wt/t -> constellation-skills-wt-t/; small checklist context/mechanical files.
- C:/Programs/constellation-skills-wt/e298-305 contained only .pytest_cache from the sandbox-visible listing; not preserved.
- C:/Programs/constellation-skills-worktrees and C:/Programs/constellation-wt-227 were empty from the sandbox-visible listing.

These paths were not registered in `git worktree list` at cleanup time.

# scripts.verify_worktree_isolation
scripts/verify_worktree_isolation.py, 178 lines, 4 holes

Verify git worktree isolation is real before — and inside — a parallel wave.

The Agent-tool `isolation:"worktree"` parameter is a harness primitive that is a
silent no-op on Windows: subagents launched with it share the single checkout and
collide. Constellation's fix is to stop trusting that flag — the Admiral
provisions a real worktree per Commander with `git worktree add` (which works on
Windows) and hands over the absolute path. This script is the mechanical check on
top of that discipline. See `skills/admiral/references/fleet-doctrine.md`,
"Worktree isolation is a harness no-op on Windows".

Two modes:

  verify_worktree_isolation.py PATH [PATH ...]
      The Admiral's pre-wave gate. Every PATH must exist, be a registered git
      worktree, and be distinct from every other PATH and from the primary (main)
      checkout. Exit 0 if isolation is real for the whole wave, else 1.

  verify_worktree_isolation.py --here EXPECTED
      A Commander's first-step self-check: assert this session's
      `git rev-parse --show-toplevel` is EXPECTED — "am I really in my assigned
      worktree, or did I land in the shared checkout?". Exit 0/1.

The gate is the mechanical guarantee; `--here` is owner-side risk-reduction whose
result the Commander pastes into its return report.

imports stdlib: __future__.annotations, argparse, os, subprocess, sys
imported by: none found

- [_utf8_stdio](_utf8_stdio.md) function: HOLE: no docstring
- [normalize_path](normalize_path.md) function: Canonicalize a path for comparison: an absolute real path (symlinks and
- [parse_worktree_list](parse_worktree_list.md) function: The registered worktree paths from `git worktree list --porcelain` output.
- [check_distinct_real](check_distinct_real.md) function: The pure multi-path decision. `provisioned_paths` are the paths the Admiral
- [check_here](check_here.md) function: The pure --here decision: is the current worktree the expected one?
- [_git](_git.md) function: Run a read-only git command and return its stripped stdout.
- [registered_worktrees](registered_worktrees.md) function: HOLE: no docstring
- [primary_checkout](primary_checkout.md) function: The main checkout: the parent of the common git dir. Ordering-independent,
- [current_toplevel](current_toplevel.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring

# scripts.agent_work_root
scripts/agent_work_root.py, 150 lines, 1 holes

Resolve the DURABLE `.agent-work` root that survives `git worktree remove`.

The recursive-improvement trio (LESSONS.md, AGENT_FEEDBACK.md,
CONSTELLATION_FEEDBACK.md, plus their sidecar/inbox ledgers) must be shared by
every linked worktree of a repo, not scattered into each worktree's own
(gitignored, disposable) `.agent-work/`. `durable_root(start)` returns the MAIN
checkout root when `start` is inside a LINKED git worktree, and otherwise returns
`start` (or cwd) UNCHANGED — a plain checkout, a non-git directory, or any git
error all fall back visibly to current behavior. It never raises and never
invents a wrong root.

One exception overrides the linked-worktree redirect: when an ACTIVE Admiral epic
lease exists in the main checkout, the main checkout is fenced read-only (per the
launch order), so redirecting durability there would point the feedback/archive
gate at an unwritable path. In that case `durable_root` honors the worktree (its
normal fallback) instead, letting the gate resolve worktree-local and pass. An
"active epic lease" is a `<main>/.agent-work/*/spine.json` whose `engine_session`
is a dict with `status == "active"` AND `claimed_by == "admiral"` (compared
case-insensitively, stripped). There is deliberately NO staleness gate — the lease
is `active`/`released` only; `last_heartbeat` is not consulted. The scan is fully
defensive (empty glob, missing/unreadable/invalid `spine.json`, absent
`engine_session` are all skipped) so `durable_root` still never raises.

The main checkout is the parent of the common git dir
(`dirname(abspath(git rev-parse --git-common-dir))`) — the same rule
`verify_worktree_isolation.py:primary_checkout()` uses. A LINKED worktree is
detected by a normalized `git rev-parse --git-dir` differing from
`--git-common-dir`; in a plain checkout the two are the same path.

imports stdlib: __future__.annotations, json, os, pathlib.Path, subprocess, sys
imported by: none found

- [_utf8_stdio](_utf8_stdio.md) function: HOLE: no docstring
- [_normalize](_normalize.md) function: Canonical form for comparison: absolute real path, drive-case and separators
- [_git_rev_parse](_git_rev_parse.md) function: Read-only `git -C base rev-parse <arg>`, run with cwd=base so relative
- [_active_epic_lease](_active_epic_lease.md) function: True iff the main checkout holds an ACTIVE Admiral epic lease.
- [durable_root](durable_root.md) function: The durable checkout root for `.agent-work` resolution.
- [durable_agent_work](durable_agent_work.md) function: Convenience: `durable_root(start) / ".agent-work"`.

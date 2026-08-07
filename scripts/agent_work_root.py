#!/usr/bin/env python
"""Resolve the DURABLE `.agent-work` root that survives `git worktree remove`.

The durable run-record artifacts (CONSTELLATION_FEEDBACK.md, plus its sidecar
ledger) must be shared by
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
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


def _normalize(path: str) -> str:
    """Canonical form for comparison: absolute real path, drive-case and separators
    folded — same idiom as `verify_worktree_isolation.normalize_path`."""
    return os.path.normcase(os.path.realpath(path))


def _git_rev_parse(base: str, arg: str) -> str:
    """Read-only `git -C base rev-parse <arg>`, run with cwd=base so relative
    outputs resolve against `base`. Raises RuntimeError on non-zero exit, and
    lets OSError (git absent / bad cwd) propagate — both caught by the caller."""
    result = subprocess.run(
        ["git", "rev-parse", arg],
        cwd=base,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git rev-parse {arg} failed in {base}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def _active_epic_lease(main_checkout: str | os.PathLike[str]) -> bool:
    """True iff the main checkout holds an ACTIVE Admiral epic lease.

    Scans `<main_checkout>/.agent-work/*/spine.json` for an `engine_session` dict
    with `status == "active"` AND `claimed_by == "admiral"` (case-insensitive,
    stripped). No staleness gate — `last_heartbeat` is not consulted. Fully
    defensive: an empty glob, or a `spine.json` that is missing, unreadable,
    invalid JSON, non-dict, or lacking a dict `engine_session`, is skipped. Never
    raises — any unexpected error scanning a file falls back to skipping it."""
    agent_work = Path(main_checkout) / ".agent-work"
    try:
        # Materialize with list() INSIDE the try so an OSError raised while
        # walking the directory (not just at glob-call time) is caught here and
        # cannot escape mid-iteration below — the "never raises" contract holds.
        spines = list(agent_work.glob("*/spine.json"))
    except OSError:
        return False
    for spine in spines:
        try:
            data = json.loads(spine.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # missing/unreadable/invalid JSON: skip this spine
        if not isinstance(data, dict):
            continue
        session = data.get("engine_session")
        if not isinstance(session, dict):
            continue
        status = str(session.get("status", "")).strip().lower()
        claimed_by = str(session.get("claimed_by", "")).strip().lower()
        if status == "active" and claimed_by == "admiral":
            return True
    return False


def durable_root(start: str | os.PathLike[str] | None = None) -> Path:
    """The durable checkout root for `.agent-work` resolution.

    Returns the MAIN checkout root only when `start` sits inside a LINKED git
    worktree. For a plain checkout, a non-git directory, or ANY git error, returns
    `start` (or cwd) unchanged. Never raises.
    """
    fallback = Path(start) if start is not None else Path.cwd()
    base = os.path.abspath(os.fspath(fallback))
    try:
        git_dir = _git_rev_parse(base, "--git-dir")
        common_dir = _git_rev_parse(base, "--git-common-dir")
    except (OSError, RuntimeError):
        # git absent, `start` not a directory, or not a git repo: fail VISIBLY to
        # current behavior — never write a wrong root.
        return fallback

    # `--git-dir` / `--git-common-dir` may be relative to `base`; join resolves
    # both relative and absolute forms. Normalize only for the comparison.
    if _normalize(os.path.join(base, git_dir)) == _normalize(os.path.join(base, common_dir)):
        return fallback  # plain checkout: the two dirs coincide

    # Linked worktree: main checkout = parent of the common git dir.
    common_abs = os.path.abspath(os.path.join(base, common_dir))
    main_checkout = os.path.dirname(common_abs)

    # Under an active Admiral epic lease the main checkout is fenced read-only, so
    # honor the worktree (the fallback) instead of redirecting to an unwritable
    # root. Absent such a lease, durability centralizes on the main checkout.
    if _active_epic_lease(main_checkout):
        return fallback
    return Path(main_checkout)


def durable_agent_work(start: str | os.PathLike[str] | None = None) -> Path:
    """Convenience: `durable_root(start) / ".agent-work"`."""
    return durable_root(start) / ".agent-work"


if __name__ == "__main__":
    print(durable_root())

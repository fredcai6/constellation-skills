#!/usr/bin/env python
"""Verify git worktree isolation is real before — and inside — a parallel wave.

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
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


def normalize_path(p: str) -> str:
    """Canonicalize a path for comparison: an absolute real path (symlinks and
    Windows junctions resolved by realpath) with drive-case and `/` vs `\\`
    separators folded by normcase. Two strings naming the same location compare
    equal after this."""
    return os.path.normcase(os.path.realpath(p))


def parse_worktree_list(porcelain: str) -> list[str]:
    """The registered worktree paths from `git worktree list --porcelain` output.
    Each record opens with a `worktree <path>` line; the `HEAD`, `branch`, `bare`,
    `detached`, and blank lines that follow are ignored."""
    paths = []
    for line in porcelain.splitlines():
        if line.startswith("worktree "):
            paths.append(line[len("worktree "):].strip())
    return paths


def check_distinct_real(
    provisioned_paths: list[str], registered: list[str], primary: str
) -> tuple[bool, str]:
    """The pure multi-path decision. `provisioned_paths` are the paths the Admiral
    created; `registered` is `parse_worktree_list` output; `primary` is the main
    checkout. Every provisioned path must be registered, none may be the primary,
    and no two may resolve to the same worktree. Returns (ok, reason); reason is
    "" when ok and names the offending path otherwise."""
    registered_norm = {normalize_path(r) for r in registered}
    primary_norm = normalize_path(primary)
    seen: dict[str, str] = {}
    for raw in provisioned_paths:
        norm = normalize_path(raw)
        if norm == primary_norm:
            return False, f"{raw} is the main checkout, not an isolated worktree"
        if norm not in registered_norm:
            return False, f"{raw} is not a registered git worktree"
        if norm in seen:
            return False, f"{raw} and {seen[norm]} resolve to the same worktree"
        seen[norm] = raw
    return True, ""


def check_here(actual_toplevel: str, expected: str) -> tuple[bool, str]:
    """The pure --here decision: is the current worktree the expected one?"""
    if normalize_path(actual_toplevel) == normalize_path(expected):
        return True, ""
    return (
        False,
        f"you are in {actual_toplevel}, not your assigned worktree {expected} — "
        f"run every git operation inside {expected}",
    )


def _git(*args: str) -> str:
    """Run a read-only git command and return its stripped stdout."""
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def registered_worktrees() -> list[str]:
    return parse_worktree_list(_git("worktree", "list", "--porcelain"))


def primary_checkout() -> str:
    """The main checkout: the parent of the common git dir. Ordering-independent,
    unlike trusting the first `git worktree list` entry (undefined for a bare
    repo)."""
    common = _git("rev-parse", "--git-common-dir")
    return os.path.dirname(os.path.abspath(common))


def current_toplevel() -> str:
    return _git("rev-parse", "--show-toplevel")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "paths", nargs="*", help="provisioned worktree paths to verify (gate mode)"
    )
    parser.add_argument(
        "--here", metavar="EXPECTED",
        help="self-check: assert the current worktree is EXPECTED",
    )
    args = parser.parse_args(argv)

    if args.here is not None:
        if args.paths:
            parser.error("--here takes no positional PATH arguments")
        try:
            actual = current_toplevel()
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        ok, reason = check_here(actual, args.here)
        if ok:
            print(f"worktree OK: in {args.here}")
            return 0
        print(f"wrong worktree: {reason}", file=sys.stderr)
        return 1

    if not args.paths:
        parser.error("give one or more worktree paths, or --here EXPECTED")

    missing = [p for p in args.paths if not os.path.isdir(p)]
    if missing:
        for p in missing:
            print(f"worktree path does not exist: {p}", file=sys.stderr)
        return 1

    try:
        registered = registered_worktrees()
        primary = primary_checkout()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    ok, reason = check_distinct_real(args.paths, registered, primary)
    if ok:
        print(f"worktree isolation verified: {len(args.paths)} distinct worktrees")
        return 0
    print(f"worktree isolation NOT verified: {reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

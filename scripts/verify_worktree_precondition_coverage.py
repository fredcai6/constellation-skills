#!/usr/bin/env python
"""Verify every worktree-entering role's spine wires the worktree-isolation gate.

The prose invariant ("a Commander's first step is to verify it is running in
its provisioned worktree") is only real once it is a command precondition on
the role's spine, not a sentence a human or agent can silently skip (#329).
This script is the enumeration side of that fix: it fails when a
worktree-entering template does NOT carry the wired precondition, catching
a template that was simply left out when the invariant was wired (the #392
shape this issue exists to prevent).

WORKTREE_ENTERING_GATES below is an explicit, hand-maintained list, not an
auto-detector, and that is deliberate. Which roles actually get dispatched
into an isolated worktree is an architectural fact about the fleet -- it is
decided by who provisions worktrees and who gets launched into one via an
Admiral LAUNCH_ORDER -- and that fact is not recoverable by scanning a
spine's JSON content:

  - Admiral provisions a real worktree per Commander (`git worktree add`)
    but does not itself enter one -- Admiral stays in the primary checkout,
    so ADMIRAL_SPINE.template.json carries no such precondition and never
    should.
  - Commander is the one role actually dispatched INTO an isolated worktree
    -- COMMANDER_SPINE.template.json's `init` gate is the one entry today.
  - Explorer is human-synchronous / upstream-only and is never delegated
    into a worktree -- EXPLORER_SPINE.template.json carries no such
    precondition either.
  - Crew (Implementer/Reviewer/Prototyper) run inside the Commander's
    already-isolated worktree; they do not provision or enter a new one of
    their own, so they have no c0-equivalent precondition to carry.

Adding a new worktree-entering role means adding its (template, gate) pair
to this list BY HAND. That is a known, accepted limit -- not something this
script silently covers by inference -- see issue #422/#329.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# (template path relative to --root, gate id) pairs that must carry the
# worktree-isolation precondition. See the module docstring for why this is
# a maintained list and not derived from scanning template content.
WORKTREE_ENTERING_GATES: tuple[tuple[str, str], ...] = (
    ("skills/commander/templates/COMMANDER_SPINE.template.json", "init"),
)

# The marker that identifies a condition as wiring the worktree-isolation
# check -- matched against behaviour (the command actually run), never
# against a description string that merely claims to run it.
ISOLATION_SCRIPT_MARKER = "verify_worktree_isolation.py"


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


class CoverageError(Exception):
    """Raised when a worktree-entering template is missing the wired precondition."""


def _condition_wires_isolation(cond: dict) -> bool:
    """True if `cond` is a command check that runs verify_worktree_isolation.py
    and is unmet by default (a shipped template must never pre-satisfy its own
    check -- that would defeat the gate for every run instantiated from it)."""
    check = cond.get("check")
    if not isinstance(check, dict):
        return False
    if check.get("kind") != "command":
        return False
    if ISOLATION_SCRIPT_MARKER not in check.get("command", ""):
        return False
    return cond.get("satisfied") is False


def _gate_wires_isolation(gate: dict) -> bool:
    for which in ("preconditions", "postconditions"):
        for cond in gate.get(which, []) or []:
            if _condition_wires_isolation(cond):
                return True
    return False


def verify_coverage(root: Path) -> int:
    """Check every listed (template, gate) pair. Returns the count checked on
    success; raises CoverageError naming every offending template/gate on
    failure (never a bare "FAIL" -- see references/global-orchestrator.md,
    "A check that cannot fail" -- state the count, name the gap)."""
    problems: list[str] = []
    for rel_path, gate_id in WORKTREE_ENTERING_GATES:
        path = root / rel_path
        if not path.is_file():
            problems.append(f"{rel_path}: template file not found")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"{rel_path}: unparseable JSON ({exc})")
            continue
        gate = data.get("tasks", {}).get(gate_id)
        if gate is None:
            problems.append(f"{rel_path}: gate {gate_id!r} not found")
            continue
        if not _gate_wires_isolation(gate):
            problems.append(
                f"{rel_path}: gate {gate_id!r} does not wire an unmet-by-default "
                f"command precondition/postcondition whose command contains "
                f"{ISOLATION_SCRIPT_MARKER!r}"
            )
    if problems:
        raise CoverageError("\n".join(problems))
    return len(WORKTREE_ENTERING_GATES)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="project root (default cwd)")
    args = parser.parse_args(argv)

    try:
        count = verify_coverage(args.root)
    except CoverageError as exc:
        print("worktree-precondition coverage FAILED:", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1

    print(f"worktree-precondition coverage OK: {count} worktree-entering template(s) checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
